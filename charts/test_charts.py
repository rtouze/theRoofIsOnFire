"""
Django test file for the charts app.
"""

from datetime import date, timedelta
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User

from charts.models import ChartProject, Task
from views import UserForm

# {{{ TODOLIST
# TODO - check user authentification in all views
# TODO - create custom permission to avoid lots of function based testing
# }}}

# {{{ UserTest
class UserTest(TestCase):
    """ TestCase related to user creation."""
    def setUp(self):
        self.user = create_user1()

    def test_unicode_method(self):
        """
        Tests that unicode return expected field (nickname).
        """
        self.assertEqual('testUser', self.user.username)
        self.assertEqual('foo', self.user.last_name)
        self.assertEqual('bar', self.user.first_name)
        self.assertEqual('foo.bar@example.com', self.user.email)
        self.assertNotEqual('passwd', self.user.password)
        self.assertEqual('testUser', unicode(self.user))

    def tearDown(self):
        self.user.delete()
# }}}

# {{{ UserFormCreationTest
class UserFormCreationTest(TestCase):
    """This class tests UserForm validation with different sets of data."""
    def test_valid_form(self):
        """" This method checks that the overriden method is_valid works."""
        data = {
            'username':'testUser2',
            'last_name':'bar',
            'first_name':'baz',
            'email':'logan@example.com',
            'password':'passwd',
            'password_check':'passwd'
        }
        form = UserForm(data)
        self.assertTrue(form.is_valid())

    def test_password_check(self):
        """ This methods checks that the 2 occurences of entered password are
        compared."""
        data = {
            'username':'testUser2',
            'last_name':'bar',
            'first_name':'baz',
            'email':'logan@example.com',
            'password':'passwd',
            'password_check':'toto'
        }
        form = UserForm(data)
        self.assertFalse(form.is_valid())

    def test_non_mandatory_names(self):
        """ Check that non required parameters are not checked by is_valid
        method."""
        data = {
            'username':'testUser2',
            'email':'logan@example.com',
            'password':'passwd',
            'password_check':'passwd'
        }
        form = UserForm(data)
        self.assertTrue(form.is_valid())
# }}}

# {{{ SignInValidationRequest

class SignInValidationRequest(TestCase):
    """ Sigin Test based on http request handling."""

    def test_valid_signin(self):
        """Check that a user is created by requesting /charts/valid_signin."""
        data = {
            'username':'testUser3',
            'last_name':'bar',
            'first_name':'baz',
            'email':'logan@example.com',
            'password':'passwd',
            'password_check':'passwd'
        }
        client = Client()
        client.post('/charts/valid_signin', data)
        actualUser = User.objects.filter(username='testUser3')[0]
        self.assertEqual('bar', actualUser.last_name)
# }}}

# {{{ UserModificationTest
class UserModificationTest(TestCase):
    """Blah Blah Blah"""

    def setUp(self):
        self.user = create_user1()

    def test_user_modification(self):
        data = {
            'first_name': 'John',
            'last_name': 'Doe'
        }
        client = Client()
        client.login(username='testUser', password='passwd')
        client.post('/charts/user/edit/{0}'.format(self.user.pk), data)
        new_user = User.objects.get(pk=self.user.pk)
        self.assertEqual('John', new_user.first_name)
        self.assertEqual('Doe', new_user.last_name)

    def tearDown(self):
        self.user.delete()

# }}}

# {{{ AccessToDashboard
class AccessToDashboard(TestCase):
    """ Test case for user dashboard access."""
    def test_mandatory_permission(self):
        """ Tests that a user can access its dashboard only if he is logged in
        and is he is the owner of the dashboard."""

        user = create_user1()
        client = Client()
        url = '/charts/dashboard/%d' % user.pk
        response = client.get(url, follow=True)
        self.assertEqual(200, response.status_code)
        if response.redirect_chain:
            redirect_url = response.redirect_chain[0][0]
            expected_url = ('http://testserver/login/invalid/unknown'
            '?next=/charts/dashboard/1')
            self.assertEqual(expected_url, redirect_url)
        else:
            self.fail('User is not redirected')

    def test_dashboard(self):
        """It tests that a valid user can access the dashboard."""
        user = create_user1()
        client = Client()
        client.login(username='testUser', password='passwd')
        response = client.get('/charts/dashboard/%d' % user.pk)
        self.assertEqual(200, response.status_code)

    def test_dashboard_with_wrong_url(self):
        """Just in case... testing the route."""
        user = create_user1()
        client = Client()
        response = client.get('/charts/dashboard/%d/' % user.pk)
        self.assertEqual(404, response.status_code)
# }}}

# {{{ Authentication verification
class AuthenticationVerification(TestCase):
    """Test that the authentication is activated for all needed pages"""
    def setUp(self):
        self.user = create_user1()
        self.client = Client()
        self.project = self._create_project()
        self.pages = [
            '/charts/dashboard/{0}',
            '/charts/project/new/{0}',
            '/charts/project/edit/{0}/{1}',
            '/charts/project/{0}/{1}',
            '/charts/project/remove/{0}/{1}'
        ]

    def _create_project(self):
        """Create and return a test project"""
        project = ChartProject();
        project.name = 'test'
        project.start_date = date.today()
        project.end_date = date.today() + timedelta(days=30)
        project.admin = self.user;
        project.save()
        return project

    def test_page_access(self):
        """Test the authentified access for every page"""
        for page in self.pages:
            self._check_page_auth(page)

    def _check_page_auth(self, page):
        """Check  that page access is authentified"""
        # It just works! If there is more replacement than place holder, format
        # won't complain. Good boy.
        url = page.format(self.user.pk, self.project.pk)
        expected_url_base = 'http://testserver/login/invalid/unknown'
        expected_url = '?next='.join([expected_url_base, url])
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, expected_url)
# }}}

# {{{ SigninRoute
class SigninRoute(TestCase):
    """ Test case to check signin form route."""
    def test_signin_route(self):
        """Just to ensure that every defined route work"""
        client = Client()
        response = client.get('/charts/signin')
        self.assertEqual(200, response.status_code)
# }}}

# {{{ Project cases
class ProjectDataSet(object):
    """ Dataset used in project tests"""
    def __init__(self):
        self.user = create_user1()
        self.project_data = {
            'name': 'test_project',
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=10),
            'admin': self.user
        }

    def cleanup(self):
        """ Remove created user from DB."""
        self.user.delete()

    def get_user_id(self):
        """ Get the ID of the self.user."""
        return self.user.pk

    def __str__(self):
        data = (str(self.user), str(self.project_data))
        return 'user = %s, project_data = %s' % data

class ProjectBaseTestCase(TestCase):
    """ Base test case to test project creation, edition and deletion."""
    def setUp(self):
        self.client = Client()
        self.dataset = ProjectDataSet()

    def create_project(self, new_name=None):
        """ Create the project defined by self.dataset.project_data in the
        database. If new_name is provided, the name of the project will be this
        value instead of *test_project*."""
        project = ChartProject(**self.dataset.project_data)
        if new_name:
            project.name = new_name
        project.admin = self.dataset.user
        project.save()
        return project

    def tearDown(self):
        self.dataset.cleanup()
        projects = ChartProject.objects.filter(name='test_project')
        for project in projects:
            project.delete()

# {{{ ProjectCreation
class ProjectCreation(ProjectBaseTestCase):
    """ Test case for project creation"""

    def test_create_project_for_user(self):
        """This method tests project creation from model."""
        project = self.create_project()
        self.assertNotEqual(0, project.pk)

    def test_creation_form_is_reachable(self):
        """Test that project creation form has valid route."""
        user = create_user1()
        self.client.login(username='testUser', password='passwd')
        url = '/charts/project/new/%d' 
        response = self.client.get(url % self.dataset.user.pk)
        self.assertEqual(200, response.status_code)

    def test_creation_form_strict_uri(self):
        """Test that project creation form route is strictly checked"""
        url = '/charts/project/new/%d/' 
        response = self.client.get(url % self.dataset.user.pk)
        self.assertEqual(404, response.status_code)
        
    def test_create_project_from_route_unidentified(self):
        """Test that a project is created through the form"""
        url = '/charts/project/new/%d' % self.dataset.user.pk
        response = self.client.post(url, self.dataset.project_data)
        expected_url = 'http://testserver/login/invalid/unknown?next=' + url
        # I don't care about "next" part.
        actual_url = response.url.split('?')[0]
        #self.assertEqual(expected_url, actual_url)
        self.assertRedirects(response, expected_url)

    def test_create_project_from_route_authentified(self):
        user = create_user1()
        url = '/charts/project/new/%d' % self.dataset.user.pk
        self.client.login(username='testUser', password='passwd')
        response = self.client.post(url, self.dataset.project_data)
        # Just a way to check that the project is created with the right admin.
        expected_name = self.dataset.project_data['name']
        project = ChartProject.objects.filter(name=expected_name)[0]
        self.assertEqual('testUser', project.admin.username)
# }}} ProjectCreation


# {{{ ProjectEdition
class ProjectEdition(ProjectBaseTestCase):
    """ Test case for project edition """
    def setUp(self):
        super(ProjectEdition, self).setUp()
        self.user = create_user1()
        self.client.login(username='testUser', password='passwd')

    def test_edit_project_from_route(self):
        """Project edition test using the project form and the dedicated
        route."""
        project = self.create_project('name to change')
        params = (self.dataset.user.pk, project.pk)
        url = '/charts/project/edit/%d/%d' % params
        response  = self.client.post(url, self.dataset.project_data)
        self.assertNotEqual(404, response.status_code)

        projects = ChartProject.objects.filter(name='name to change')
        self.assertEqual(0, len(projects), 'name to change found!')

        expected_name = self.dataset.project_data['name']
        projects = ChartProject.objects.filter(name=expected_name)
        self.assertEqual(1, len(projects), 'test_project not found !')

    def test_edit_project_from_strict_uri(self):
        """ Test that the uri pattern isstrictly respected while requisting
        project edition page."""
        project = self.create_project('name to change')
        params = (self.dataset.user.pk, project.pk)
        url = '/charts/project/edit/%d/%d/' % params
        response  = self.client.post(url, self.dataset.project_data)
        self.assertEqual(404, response.status_code)
# }}} ProjectEdition


# {{{ ProjectDeletion
class ProjectDeletion(ProjectBaseTestCase):
    """ Test case for project deletion"""
    def setUp(self):
        super(ProjectDeletion, self).setUp()
        project = self.create_project()
        self.data = (self.dataset.user.pk, project.pk)
        self.user = create_user1()
        self.client.login(username='testUser', password='passwd')
        
    def test_delete_project_from_route(self):
        """ This methods tests that a project is deleted when requesting the
        URI. """

        # TODO - OK, user is authentified but we've to check that user = project admin
        project = self.create_project()
        self.data = (self.dataset.user.pk, project.pk)
        url = '/charts/project/remove/%d/%d' % self.data
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)
        test_name = self.dataset.project_data['name']
        projects = ChartProject.objects.filter(name=test_name)
        self.assertEqual(0, len(projects))

    def test_delete_project_from_strict_route(self):
        """ This methods tests that user get the correct response only when the
        URI is strictly respected. """
        url = '/charts/project/remove/%d/%d/' % self.data
        response = self.client.get(url)
        self.assertEqual(404, response.status_code)
# }}} ProjectDeletion


# {{{ ProjectView
class ProjectView(ProjectBaseTestCase):
    """ Test case for project read access """
    def setUp(self):
        """Blah blah"""
        super(ProjectView, self).setUp()
        user = create_user1()
        self.client.login(username='testUser', password='passwd')
        
    def test_access_from_route(self):
        """ Test the URI for project view page."""
        project = self.create_project()
        url = '/charts/project/%d/%d' % (self.dataset.user.pk, project.pk)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        
    def test_access_from_strict_route(self):
        """ Test that the URI pattern for project view page must be strictly
        respected."""
        project = self.create_project()
        url = '/charts/project/%d/%d/' % (self.dataset.user.pk, project.pk)
        response = self.client.get(url)
        self.assertEqual(404, response.status_code)
# }}} ProjectView


class ProjectTaskEdition(ProjectBaseTestCase):
    def setUp(self):
        super(ProjectTaskEdition, self).setUp()
        self.project = self.create_project('test chart project')

    def test_tasks_are_created(self):
        # TODO only use ISO date format string (yyyy-mm-dd) mixing date strings is error prone
        url = '/charts/update_tasks/{0}'.format(self.project.pk)
        expected_date = date(2014, 11, 4)
        expected_points = 10
        expected_name = 'foobar'
        data = '[{{"task_name":"{0}","points":{1},"end_date":"{2}"}}]'.format(
            expected_name,
            expected_points,
            expected_date.strftime('%m/%d/%Y'))
        response = self.client.post(url, data, content_type="text/json")
        self.assertEqual(200, response.status_code)
        new_task = Task.objects.filter(project=self.project)[0]
        self.assertEqual(expected_date, new_task.end_date)
        self.assertEqual(expected_name, new_task.task_name)
        self.assertEqual(expected_points, new_task.points)

#  }}} Project cases
        
# {{{ Test user creation
def create_user1():
    """ Creates a valid user in the database. It's name will be testUser. """
    try:
        User.objects.get(username='testUser').delete()
    except User.DoesNotExist:
        pass
    return User.objects.create_user(
                username='testUser',
                last_name='foo',
                first_name='bar',
                email='foo.bar@example.com',
                password='passwd'
                )

def create_user2():
    """ Creates a valid user in the database. It's name will be testUser. """
    try:
        User.objects.get(username='testUser').delete()
    except User.DoesNotExist:
        pass
    return User.objects.create_user(
                username='testUser2',
                last_name='foofoo',
                first_name='barbar',
                email='foo.bar2@example.com',
                password='passwd'
                )
# }}}

# vim: foldmethod=marker:

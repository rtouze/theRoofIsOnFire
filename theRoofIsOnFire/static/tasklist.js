/******************************************************************************
 * Script for theRoofIsOnFire
 *****************************************************************************/

/*jslint browser: true, plusplus: true, todo: true */

// Warning: it depends on screen resolution
var BAR_HEIGHT_FACTOR = 10;
var Y_PADDING = 20;
var SCORE_X_OFFSET = -30;
var SCORE_Y_OFFSET = -30;
var DEFAULT_TASK_TEXT = 'Something to do';

// Global fonctions
var addListenersToDOMObjects;
var createSvg;
var updateScore;
var taskEndDateCleanup;
var isDate;
var redrawGraph;
var stringToDate;
var displayBarScore;
var destroyBarScore;

$(function () {
    'use strict';
    addListenersToDOMObjects();
    createSvg();
    updateScore();
});

/**
 * This function add event listeners to objects existing in the page when it's
 * loaded by the browser.
 */
var addListenersToDOMObjects = function () {
    'use strict';

    var deleteTaskRow = function (event) {
        var calledButton = event.target,
            row = calledButton.parentNode.parentNode;
        if (row.parentNode) {
            row.parentNode.removeChild(row);
            row = null;
            updateScore();
        }
    },

        taskDoneUpdate = function (chosenDate, elem) {
            if (isDate(chosenDate) || chosenDate === '') {
                redrawGraph();
            }
        },

        addTableLine = function () {
            var $newLine = $('<tr>'),
                $newTask = $('<td contenteditable="true" name="task_name">'),
                $newScore = $('<td name="score_cell" class="score" contenteditable="true">'),
                $newDate = $('<td name="date_cell">'),
                $dateInput = $('<input type="text" class="date_input" title="Format mm/jj/aaaa">'),
                $newEraseButtonCell = $('<td class="no_border">'),
                $newEraseButtonDiv = $('<div class="form_button bold minus_button" name="erase_button" title="Remove task.">');

            $newTask.html(DEFAULT_TASK_TEXT);

            $newScore.html('0');
            $newScore.on('input', updateScore);

            $dateInput.datepicker({onClose: taskDoneUpdate});
            $newDate.append($dateInput);

            $newEraseButtonDiv.click(deleteTaskRow);
            $newEraseButtonCell.append($newEraseButtonDiv);

            $newLine.append($newTask);
            $newLine.append($newScore);
            $newLine.append($newDate);
            $newLine.append($newEraseButtonCell);

            $('#task_table').append($newLine);
        },

        syncData = function () {
            /* OK, what do we need
             * - Gather task info and put it into a JSON object
             * - Use a XHR to ask Django to put them in DB
             */
            // TODO refactoring, boy
            var tasksData = [],
                $nameCells = $('td[name=task_name]'), //document.getElementsByName('task_name'),
                projectId = $('#project_id').html(),
                splittedCookie = document.cookie.split(';'),
                csrfToken = '',
                i,
                nameCellsLength,
                childrenCellsLength,
                j,
                $children,
                points,
                endDateString,
                elem,
                xhr,
                $syncDiv,
                splittedCookieLength,
                // Stolen from wikipedia!
                getXHRObject = function () {
                    var ref = null;
                    if (window.XMLHttpRequest) {
                        ref = new window.XMLHttpRequest();
                    } else if (window.ActiveXObject) { // Older IE.
                        ref = new window.ActiveXObject("MSXML2.XMLHTTP.3.0");
                    }
                    return ref;
                };

            $nameCells.each(function () {
                points = 0;
                endDateString = "";
                $children = $(this).parent().children('td');
                $children.each(function () {
                    if ('score_cell' === $(this).attr('name')) {
                        points = Number($(this).prop('textContent'));
                    }

                    if ('date_cell' === $(this).attr('name')) {
                          $(this).children("input").each(function () {
                            endDateString = $(this).prop('value');
                          });
                        if (!isDate(endDateString)) {
                            endDateString = "";
                        }
                    }
                });

                tasksData.push(
                    {
                        'task_name': $(this).prop('textContent'),
                        'points': points,
                        'end_date': endDateString
                    }
                );
            });

            for (i = 0, splittedCookieLength = splittedCookie.length; i < splittedCookieLength; i += 1) {
                elem = splittedCookie[i];
                elem.replace(/\s+([\d\w=]*)\s+/, '$1');
                if (elem.split('=')[0] === 'csrftoken') {
                    csrfToken = elem.split('=')[1];
                    break;
                }
            }

            xhr = getXHRObject();
            xhr.onreadystatechange = function () {
                if (xhr.readyState !== 4 || xhr.status !== 200) {
                    //TODO : error
                    return;
                }
                $syncDiv = $('#sync-ok');
                $syncDiv.css('top', window.pageYOffset + 'px').toggle();
                setTimeout(function () { $syncDiv.toggle() }, 2000);
            };

            // Note: used only when using POST method
            xhr.open('POST', '/charts/update_tasks/' + projectId, true);
            xhr.setRequestHeader("X-CSRFToken", csrfToken);
            xhr.send(JSON.stringify(tasksData));
        },

        scoreCells = $("td[name=score_cell]"), 
        dateCells = $("td[name=date_cell]"), 
        eraseButtons = $("div[name=erase_button]"), 
        i,
        listLength;

    scoreCells.each(function () {
        $(this).on('input', updateScore);
    });
    dateCells.children('input').each(function () {
        // TODO : fix this shit
        $(this).datepicker(
            {onClose: taskDoneUpdate});
    });
    eraseButtons.each(function () {
        $(this).click(deleteTaskRow);
    });
    // Adds a table line when user click on '+' button
    $('#plus_btn').click(addTableLine);
    $('#sync_btn').click(syncData);
};

var calcScore = function () {
    'use strict';
    var totalScore = 0;
    $('td[name=score_cell]').each(function () {
        totalScore += Number($(this).prop('textContent'));
    });
    return totalScore;
};

updateScore = function () {
    'use strict';
    var score = calcScore();
    $('#total_score').html('Total score = ' + score.toString());
    redrawGraph();
};

var getDayDelta = function () {
    var beginDate = stringToDate($('#begin_date').html().trim()),
        endDate = stringToDate($('#end_date').html().trim());
    return (endDate.getTime() - beginDate.getTime()) / (24 * 3600000) + 1;
};

var createSvg = function () {
    'use strict';
    // We analyze the begin and end date to do the job
    var dayDelta = getDayDelta(),
        xOrigin = 50,
        // Svg graph creation (rather long)
        $svgNode = $('#svg_bd_graph'),
        svgNameSpace = 'http://www.w3.org/2000/svg',
        // Total score (so far) computation 
        score = calcScore(),
        barWidth,
        $svgContainingDiv = $('#burndown_chart'),
        i,
        Line,
        RectangleBar,
        xAxis,
        idealLine,
        verticalBar,
        element;

    $svgNode.attr('xmlns', svgNameSpace);
    $svgNode.attr('version', '1.1');

    // The bar width is calculated depending on the duration of the chart in
    // days.
    //
    // TODO - Vary with svg size
    $svgContainingDiv.css('height', Y_PADDING + score*BAR_HEIGHT_FACTOR + 'px');

    // TODO ce serait bien de ne fonctionner qu'en ratio
    barWidth = ($svgContainingDiv.width() - 85)/(2*dayDelta);

    // Axis Line definition
    Line = function (id) {
        this.id = id;
        this.x1 = 0;
        this.x2 = 0;
        this.y1 = 0;
        this.y2 = Y_PADDING + score*BAR_HEIGHT_FACTOR;
    };

    Line.prototype.getElement = function () {
        var lineElement = document.createElementNS(svgNameSpace, 'line');
        lineElement.setAttribute('id', this.id);
        lineElement.setAttribute('x1', xOrigin + this.x1);
        lineElement.setAttribute('y1', this.y1);
        lineElement.setAttribute('x2', xOrigin + this.x2);
        lineElement.setAttribute('y2', this.y2);
        return lineElement;
    };
    // End of Line definition

    // Rectangle Bar definition
    RectangleBar = function (id) {
        this.id = id;
        this.classAttr = 'bdBar';
        this.width = barWidth;
        this.height = score * BAR_HEIGHT_FACTOR;
        this.x = 0;
        this.y = Y_PADDING;
        // rx is for round shape. I don't know if I want to keep it for the moment.
        //this.rx = 5;
    };

    RectangleBar.prototype.getElement = function () {
        var verticalBarElement = document.createElementNS(svgNameSpace, 'rect');
        verticalBarElement.setAttribute('id', this.id);
        verticalBarElement.setAttribute('class', this.classAttr);
        verticalBarElement.setAttribute('width', this.width);
        verticalBarElement.setAttribute('height', this.height);
        verticalBarElement.setAttribute('x', xOrigin + this.x);
        verticalBarElement.setAttribute('y', this.y);
        verticalBarElement.setAttribute('rx', this.rx);
        return verticalBarElement;
    };
    // End of RectangleBar

    //Creation des rects
     
    for (i = 0; i < dayDelta; i += 1) {
        verticalBar = new RectangleBar('bdBar' + i);
        verticalBar.x = 10 + i*2*barWidth;
        element = verticalBar.getElement();
        element.onmouseover = displayBarScore;
        element.onmouseleave = destroyBarScore;
        $svgNode.append(element);
    }

    // Axis
    xAxis = new Line('graph_x_axis');
    xAxis.y1 = Y_PADDING + score * BAR_HEIGHT_FACTOR;
    xAxis.x2 = 20 + (dayDelta - 1) * 2 * barWidth + barWidth;
    $svgNode.append(xAxis.getElement());

    // Ideal progression line
    idealLine = new Line('graph_ideal_line');
    idealLine.y1 = Y_PADDING;
    idealLine.x2 = 10 + (dayDelta - 1)*2*barWidth + barWidth;
    $svgNode.append(idealLine.getElement());
};

displayBarScore = function (event) {
    'use strict';
    // TODO cleanup this crap: use a state to know if we actually went to another bar. Use a timeout to make the stuff disapear
    var h = event.target.attributes.height.textContent,
        displayedScore = Number(h) / BAR_HEIGHT_FACTOR,
        $barScore = $('#mouse_bar_score');
    $barScore.css('top', window.pageYOffset + SCORE_Y_OFFSET + event.clientY + 'px');
    $barScore.css('left', window.pageXOffset + SCORE_X_OFFSET + event.clientX + 'px');
    $barScore.html('Score: ' + displayedScore);
    $barScore.show();
};

destroyBarScore = function () {
    'use strict';
    window.setTimeout(function () {$('#mouse_bar_score').hide()}, 100);
};


var stringToDate = function (stringDate) {
    'use strict';
    var arrayDate = stringDate.split('/');
    return new Date(
        // January = month 0
        Number(arrayDate[2]),
        Number(arrayDate[0]) - 1 ,
        Number(arrayDate[1])
    );
};

var updateSvgHeight = function (score) {
    'use strict';
    var $xAxis = $('#graph_x_axis');

    $('#burndown_chart').css('height', Y_PADDING + score*BAR_HEIGHT_FACTOR + 'px');
    $('.bdBar').each(function () {
        $(this).attr('height', score*BAR_HEIGHT_FACTOR);
        $(this).attr('y', Y_PADDING);
    });

    $xAxis.attr('y1', Y_PADDING + score*BAR_HEIGHT_FACTOR);
    $xAxis.attr('y2', Y_PADDING + score*BAR_HEIGHT_FACTOR);
    $('#graph_ideal_line').attr('y2', Y_PADDING + score*BAR_HEIGHT_FACTOR);
};

taskEndDateCleanup = function (dateString) {
    'use strict';
    return dateString.replace(/[\n\s]*([\d\/]*)[\n\s]*/, '$1');
};

redrawGraph = function () {
    // TODO - Don't work when I edit newly created tasks
    'use strict';
    var $dateCells = $('td[name=date_cell]'),
        beginDate = stringToDate($('#begin_date').html().trim()),
        content,
        associatedScore,
        $cellsFromDateLine,
        cellsFromDateLineL,
        subDelta,
        subDeltaDays,
        currHeight,
        currY,
        updatedY,
        i,
        j,
        $scoreCell;

    // bar height is reset for the whole graph
    updateSvgHeight(calcScore());

    $dateCells.each(function () {
        $(this).children('input').each(function () {
            content = $(this).prop("value") || "";
            content = content.trim();
        })

        // TODO - break down responsabilities. height computation should not be with
        // bar display since it does not allows to test. I should create a graph model.
        // In JS? Wait… Wat?

        if (isDate(content)) {
            associatedScore = 0;
            $scoreCell = $(this).parent().children('td[name=score_cell]')[0];
            associatedScore = Number($scoreCell.textContent);
            subDelta = stringToDate(content).getTime() - beginDate.getTime();
            subDeltaDays = subDelta / (24 * 3600000);
            $cellsFromDateLine = $('.bdBar');
            cellsFromDateLineL = $('.bdBar').length;
            for (i = subDeltaDays; i < cellsFromDateLineL; ++i) {
                currHeight = Number($cellsFromDateLine[i].getAttribute('height'));
                var newHeight = currHeight - associatedScore * BAR_HEIGHT_FACTOR;
                $cellsFromDateLine[i].setAttribute(
                        'height',
                        currHeight - associatedScore * BAR_HEIGHT_FACTOR
                        );
                currY = $cellsFromDateLine[i].getAttribute('y');
                updatedY = Number(currY) + associatedScore * BAR_HEIGHT_FACTOR;
                $cellsFromDateLine[i].setAttribute('y', updatedY);
            }
        }
    });
};

isDate = function (dateString) {
    'use strict';
    var matcher = dateString.match(/\d\d\/\d\d\/\d\d\d\d/);
    return matcher && matcher[0] === dateString;
};

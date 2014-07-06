/******************************************************************************
 * Script for theRoofIsOnFire
 *****************************************************************************/

window.onload = main;

function main() {
  var bars = document.getElementsByClassName('title_bar');
  var barl = bars.length;
  console.log('DEBUG - je vais regarder les bars');

  for(i=0; i<barl; i++) {
    console.log('bar '+i);
    var bar = bars[i];
    var origin_backgound = bar.style.background;
    bar.onmouseover = function() {
      console.log('toto - ' + this.id);
      this.style.background = '#ec763c';
    };

    bar.onmouseout = function() {
      this.style.background = origin_backgound;
    }
  }
}

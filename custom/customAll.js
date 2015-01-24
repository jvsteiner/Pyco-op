var onSlider = function(e){
  var columns = $(e.currentTarget).find("td");
  var ranges = [], total = 0, i, s = "Ranges: ", w;
  for(i = 0; i<columns.length; i++){
    w = columns.eq(i).width()-10 - (i===0?1:0);
    ranges.push(w);
    total+=w;
  }
  for(i=0; i<columns.length; i++){
    ranges[i] = 100*ranges[i]/total;
    carriage = ranges[i]-w;
    s+=" "+ Math.round(ranges[i]) + "%,";
  }
  s=s.slice(0,-1);
};

var flashMessage = function(data){
  html = '';
  for (i=0; i<data.length; i++) {
    html += '<div class="alert alert-' + data[i]['type'] + '"><a href="#" class="close" data-dismiss="alert">&times;</a>' + data[i].message + '</div>';
  }
  return html;
};

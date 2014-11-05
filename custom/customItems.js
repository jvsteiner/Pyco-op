// your custom javascript goes here
// 
$(document).ready(function(){

  function OBJ2CSV(objArray) {
    var str = '';
    var line = '';
    var head = objArray[0];
    for (var index in objArray[0]) {
      line += index + ',';
    }
    line = line.slice(0, -1);
    str += line + '\r\n';
    for (var i = 0; i < objArray.length; i++) {
      var line = '';
      for (var index in objArray[i]) {
        line += objArray[i][index] + ',';
      }
      line = line.slice(0, -1);
      str += line + '\r\n';
    }
    return str;    
  }

  function ItemViewModel(config) { //for order viewing
    var self = this;
    self.items = ko.observableArray([]);
    self.status = ko.observableArray([]);

    function Item() {
      var self = this;
      self.name = ko.observable();
      self.description = ko.observable();
      self.units = ko.observable();
      self.max_available = ko.observable();
      self.price = ko.observable();
      self.active = ko.observable(true);
    }
    // Operations
    self.addItem = function() {
      self.items.push(new Item());
    };

    self.removeItem = function(item) {
      self.items.remove(item);
    };

    self.getOld = function() {
      $.getJSON("/farmers/getold", function (data) {
        // console.log(data);
        ko.mapping.fromJS(data, ivm);
        // console.log(self.old_items());
        self.items([]);
        ko.utils.arrayForEach(self.old_items(), function(old_item) {
          var the_item = new Item();
          the_item.name(old_item.name());
          the_item.description(old_item.description());
          the_item.units(old_item.units());
          the_item.max_available(old_item.max_available());
          the_item.price(old_item.price());
          the_item.active(old_item.active());
          ko.utils.arrayPushAll(self.items(), [the_item]);
          // self.items.push(the_item);
        });
        self.items.valueHasMutated();
        // console.log(ko.toJS(self.items));
      });
    };

    $.getJSON("/farmers/update", function (data) {
      ko.mapping.fromJS(data, ivm);
      // console.log(self.old_items());
      ko.utils.arrayForEach(self.old_items(), function(old_item) {
        var the_item = new Item();
        the_item.name(old_item.name());
        the_item.description(old_item.description());
        the_item.units(old_item.units());
        the_item.max_available(old_item.max_available());
        the_item.price(old_item.price());
        the_item.active(old_item.active());
        the_item.id = old_item.id();
        ko.utils.arrayPushAll(self.items(), [the_item]);
        // self.items.push(the_item);
      });
      self.items.valueHasMutated();
      // console.log(ko.toJS(self.items));
    });

    $("button#submititems").live("click", function() {
      $.post("/farmers/update", ko.toJSON(self.items()), function(returnedData) {
        self.status([JSON.parse(returnedData)]);
      })
    });

    $("button#newitem").live("click", function() {
      self.items.push(new Item())
    });

    $("button#getold").live("click", function() {
      self.getOld();
    });

    $("button#download").click(function() {
      var csv = OBJ2CSV(ko.toJS(self.items));      
      window.open("data:text/csv;charset=utf-8," + escape(csv))
    });

    if(isAPIAvailable()) {
      $('#files').bind('change', handleFileSelect);
    }

    function handleFileSelect(evt) {
      var files = evt.target.files; // FileList object
      var file = files[0];
      printTable(file);
    }

    function printTable(file) {
      var reader = new FileReader();
      reader.readAsText(file);
      reader.onload = function(event){
        var csv = event.target.result;
        var data = $.csv.toObjects(csv, { onParseValue: $.csv.hooks.castToScalar });  
        // console.log(data);
        self.items(data);
      };
      reader.onerror = function(){ alert('Unable to read ' + file.fileName); };
    }

    var parseBool = function (value)
    {
      if (value == "true")
      {
        return true;
      }
      else if (value == "false")
      {
        return false;
      }
      else
      {
        return value;
      }
    }
    // $("button#upload").click(function() {
    //   if (window.File && window.FileReader && window.FileList && window.Blob) {
    //     document.getElementById('upload').addEventListener('change', readSingleFile, false);
    //   } else {
    //     alert('The File APIs are not supported by your browser.');
    //   }
    // });

    ko.mapping.fromJS(config, {}, self);
  }

  ko.bindingHandlers.currency = {
    symbol: ko.observable('€'),
    update: function(element, valueAccessor, allBindingsAccessor){
      return ko.bindingHandlers.text.update(element,function(){
        var value = +(ko.utils.unwrapObservable(valueAccessor()) || 0),
          symbol = ko.utils.unwrapObservable(allBindingsAccessor().symbol === undefined
                      ? allBindingsAccessor().symbol
                      : ko.bindingHandlers.currency.symbol);
        return symbol + value.toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,");
      });
    }
  };

  var ivm = new ItemViewModel({'old_items': []});
  ko.applyBindings(ivm,$("#myitems")[0]);


  $("#test").colResizable({
    liveDrag:true, 
    draggingClass:"rangeDrag", 
    gripInnerHtml:"<div class='rangeGrip'></div>", 
    onResize:onSlider,
    minWidth:8
  }); 

  var onSlider = function(e){
    var columns = $(e.currentTarget).find("td");
    var ranges = [], total = 0, i, s = "Ranges: ", w;
    for(i = 0; i<columns.length; i++){
      w = columns.eq(i).width()-10 - (i==0?1:0);
      ranges.push(w);
      total+=w;
    }    
    for(i=0; i<columns.length; i++){      
      ranges[i] = 100*ranges[i]/total;
      carriage = ranges[i]-w
      s+=" "+ Math.round(ranges[i]) + "%,";     
    }   
    s=s.slice(0,-1);    
  }

});


  function isAPIAvailable() {
    // Check for the various File API support.
    if (window.File && window.FileReader && window.FileList && window.Blob) {
      // Great success! All the File APIs are supported.
      return true;
    } else {
      // source: File API availability - http://caniuse.com/#feat=fileapi
      // source: <output> availability - http://html5doctor.com/the-output-element/
      document.writeln('The HTML5 APIs used in this form are only available in the following browsers:<br />');
      // 6.0 File API & 13.0 <output>
      document.writeln(' - Google Chrome: 13.0 or later<br />');
      // 3.6 File API & 6.0 <output>
      document.writeln(' - Mozilla Firefox: 6.0 or later<br />');
      // 10.0 File API & 10.0 <output>
      document.writeln(' - Internet Explorer: Not supported (partial support expected in 10.0)<br />');
      // ? File API & 5.1 <output>
      document.writeln(' - Safari: Not supported<br />');
      // ? File API & 9.2 <output>
      document.writeln(' - Opera: Not supported');
      return false;
    }
  }



/*
JSON SAMPLE = {
  'order': [{
    'farmer': 'farmername',
    'items': [{
      'name': 'itemname',
      'description': 'itemdescription',
      'price': 'itemprice',
      'quantity_per_unit': 'itemquantity_per_unit',
      'units': 'units sold in (ie. 100g)',
      'available': 'items_available'
    }, {more_items...}]
  }, {more_farmers...}]
}*/
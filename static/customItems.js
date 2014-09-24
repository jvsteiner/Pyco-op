// your custom javascript goes here
// 
$(document).ready(function(){

  function ItemViewModel(config) { //for order viewing
    var self = this;
    self.items = ko.observableArray([]);
    self.status = ko.observable();

    function Item() {
      var self = this;
      self.name = ko.observable(0);
      self.description = ko.observable(0);
      self.units = ko.observable(0);
      self.max_available = ko.observable(0);
      self.price = ko.observable(0);
      self.active = ko.observable(0);
    }
    // Operations
    self.addItem = function() {
      self.items.push(new Item());
    };

    self.removeItem = function(item) {
      self.items.remove(item);
    };

    $.getJSON("/farmers/update", function (data) {
      // console.log(data);
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
      // console.log(self.items());
    });

    $("button#submititems").live("click", function() {
      $.post("/farmers/update", ko.toJSON(self.items()), function(returnedData) {
        console.log(returnedData);
        self.status(returnedData);
      })
    });
    $("button#newitem").live("click", function() {
      self.items.push(new Item())
    });
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

});
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
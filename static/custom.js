// your custom javascript goes here
// 
$(document).ready(function(){
  function Order(id, description, units) {
    var self = this;
    self.id = id;
    self.description = description;
    self.units = units;
    self.quantity = ko.observable('');
  }

  function ItemViewModel(config) { //for order viewing
    var self = this;
    self.orders = ko.observableArray([]);
    // Operations
    self.addOrder = function(id, description, units) {
      var theItem = new Order(id, description, units);
      var match = ko.utils.arrayFirst(self.orders(), function(item) {
        return theItem.id === item.id;
      });

      if (!match) {
        self.orders.push(theItem);
      }
    };
    self.removeOrder = function(id) {
      self.orders.remove(function(item) { return item.id === id })
    };

    $("button#submitorder").live("click", function() {
      $.post("/order/update", JSON.stringify(self.orders()), function(returnedData) {
        console.log(returnedData);
      })
    });
    ko.mapping.fromJS(config, {}, self);
  }

  var ivm = new ItemViewModel({'items': []});
  ko.applyBindings(ivm,$("#myitems")[0]);

  // var ivm = new ItemViewModel();
  $.getJSON("/order/update", function (data) {
    // console.log(data);
    ko.mapping.fromJS(data, ivm);
  });


  $("button#submititems").live("click", function() {
    // ws.send(JSON.stringify({'action': {'type': 'LOGIN', 'userid': self.username(), 'password': 'test12'}}));
  });
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
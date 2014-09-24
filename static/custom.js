// your custom javascript goes here
// 
$(document).ready(function(){

  function ItemViewModel(config) { //for order viewing
    var self = this;
    self.orders = ko.observableArray([new Order(1,'a','b',1)]);
    self.total = ko.computed(function(){
      var tot=0;
      ko.utils.arrayForEach(self.orders(), function(order) {
          tot += order.subtotal();
      });
      return tot
    }, self);

    function Order(id, description, units, price) {
      var self = this;
      self.id = id;
      self.description = description;
      self.units = units;
      self.price = price;
      self.quantity = ko.observable(0);
      self.subtotal = ko.computed(function() {
        return self.price * self.quantity();
      }, self);
    }
    // Operations
    self.addOrder = function(id, description, units, price) {
      var theItem = new Order(id, description, units, price);
      var match = ko.utils.arrayFirst(self.orders(), function(item) {
        return theItem.id === item.id;
      });
      if (!match) {
        self.orders.push(theItem);
      };
    };
    self.removeOrder = function(id) {
      self.orders.remove(function(item) { return item.id === id })
    };

    $("button#submitorder").live("click", function() {
      $.post("/order/update", ko.toJSON(self.orders()), function(returnedData) {
        console.log(returnedData);
      })
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
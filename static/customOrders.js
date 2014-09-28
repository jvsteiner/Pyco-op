// your custom javascript goes here
// 
$(document).ready(function(){

  function OrderViewModel(config) { //for order viewing
    var self = this;
    self.orders = ko.observableArray([]);
    self.status = ko.observableArray([]);
    self.total = ko.computed(function(){
      var tot=0;
      ko.utils.arrayForEach(self.orders(), function(order) {
          tot += order.subtotal();
      });
      return tot
    }, self);

    function Order(item_id, name, units, price) {
      var self = this;
      self.item_id = item_id;
      self.name = name;
      self.units = units;
      self.price = price;
      self.quantity = ko.observable(0);
      self.subtotal = ko.computed(function() {
        return self.price * self.quantity();
      }, self);
    }
    // Operations
    self.addOrder = function(item_id, name, units, price) {
      var theItem = new Order(item_id, name, units, price);
      var match = ko.utils.arrayFirst(self.orders(), function(item) {
        return theItem.item_id === item.item_id;
      });
      if (!match) {
        self.orders.push(theItem);
      };
    };
    self.removeOrder = function(item_id) {
      self.orders.remove(function(item) { return item.item_id === item_id })
    };

    $.getJSON("/order/update", function (data) {
      ko.mapping.fromJS(data, ovm);
      ko.utils.arrayForEach(self.old_orders(), function(old_order) {
        var the_order = new Order(old_order.item_id(), old_order.name(), old_order.units(), old_order.price());
        the_order.quantity(old_order.quantity());
        the_order.id = old_order.id();
        ko.utils.arrayPushAll(self.orders(), [the_order]);
        // self.orders.push(the_order);
      });
      self.orders.valueHasMutated();
    });

    $("button#submitorder").live("click", function() {
      $.post("/order/update", ko.toJSON(self.orders()), function(returnedData) {
        self.status([JSON.parse(returnedData)]);
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

  var ovm = new OrderViewModel({'items': [], 'orders': []});
  ko.applyBindings(ovm,$("#myorders")[0]);

  // var ovm = new OrderViewModel();

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
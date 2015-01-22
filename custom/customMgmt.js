$(document).ready(function(){

  function MgmtViewModel(config) { //for order viewing
    var self = this;
    self.orders = ko.observableArray([]);
    self.status = ko.observableArray([]);
    self.user = ko.observable();
    self.userorders = ko.observableArray([]);
    self.total = ko.computed(function(){
      var tot=0;
      ko.utils.arrayForEach(self.userorders(), function(order) {
          tot += order.subtotal();
      });
      return tot;
    }, self);

    function Order(item_id, name, units, price, user, user_id) {
      var self = this;
      self.item_id = item_id;
      self.name = name;
      self.units = units;
      self.price = price;
      self.user = user;
      self.user_id = user_id;
      self.quantity = ko.observable(0);
      self.subtotal = ko.computed(function() {
        return self.price * self.quantity();
      }, self);
    }
    // Operations

    self.filterOrders = function() {
      self.userorders.removeAll();
      ko.utils.arrayForEach(self.orders(), function(order){
        if (order.user == self.user()) {
          ko.utils.arrayPushAll(self.userorders(), [order]);
        }
      });
      self.userorders.valueHasMutated();
    };

    $.getJSON("/manage/update", function (data) {
      ko.mapping.fromJS(data, mvm);
      ko.utils.arrayForEach(self.old_orders(), function(old_order) {
        var the_order = new Order(old_order.item_id(), old_order.name(), old_order.units(), old_order.price(), old_order.user(), old_order.user_id());
        the_order.quantity(old_order.quantity());
        the_order.id = old_order.id();
        ko.utils.arrayPushAll(self.orders(), [the_order]);
        // self.orders.push(the_order);
      });
      self.orders.valueHasMutated();
    });

    $("button#submitorder").on("click", function() {
      $.post("/manage/update", ko.toJSON(self.userorders()), function(returnedData) {
        self.status([JSON.parse(returnedData)]);
      });
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

  var mvm = new MgmtViewModel({'buyers': [], 'orders': []});
  ko.applyBindings(mvm,$("#mgmt")[0]);

  $(".resizable").colResizable({
    liveDrag:true,
    draggingClass:"rangeDrag",
    gripInnerHtml:"<div class='rangeGrip'></div>",
    onResize:onSlider,
    minWidth:8
  });
});
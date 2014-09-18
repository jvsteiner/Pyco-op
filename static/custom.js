// your custom javascript goes here
// 
var ItemViewModel = function (config) { //for order viewing
  var self = this;


};

var mvm = new ItemViewModel({'order': [{'items': []}], 'myitems': []);
ko.applyBindings(mvm,$("#myitems")[0]);

$("button#submititems").live("click", function() {
  // ws.send(JSON.stringify({'action': {'type': 'LOGIN', 'userid': self.username(), 'password': 'test12'}}));
});
$("button#submitorder").live("click", function() {
  // ws.send(JSON.stringify({'action': {'type': 'LOGIN', 'userid': self.username(), 'password': 'test12'}}));
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
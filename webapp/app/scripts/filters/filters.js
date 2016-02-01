app.filter('link', function() {
  return function(value) {
    return (!value) ? '' : angular.lowercase(value.replace(/ /g, ''));
  };
});

app.filter('nospace', function() {
  return function(value) {
    return (!value) ? '' : value.replace(/ /g, '');
  };
});

app.filter('hidemaildomain', function() {
  return function(value) {
    return (!value) ? '' : value.replace(/@.*/g, '');
  };
});

app.filter('NA', function() {
  return function(value) {
    return (value == null || value == "") ? "NA" : value;
  };
});

app.filter('empty', function() {
  return function(value) {
    return (value == null || value == "null" || value == "") ? "" : value;
  };
});


app.filter('totalVaue', function() {
  return function(data, key) {
    if (typeof(data) === 'undefined' && typeof(key) === 'undefined') {
      return 0;
    }
    if (typeof data == 'undefined') {
      return;
    }
    var sum = 0;
    for (var i = 0; i < data.length; i++) {
      sum = sum + data[i][key];
    }

    var ind = "";
    if (sum > 999999) {
      sum = (sum / 1000000);
      ind = "M";
    } else if (sum > 999) {
      sum = (sum / 1000);
      ind = "K";
    }

    var returnData = sum.toFixed(2) + ind;

    return returnData;
  }
});

app.filter('kiloMil', function() {
  return function(data) {
    if (typeof(data) === 'undefined' && typeof(key) === 'undefined') {
      return 0;
    }
    var ind = "";
    if (data > 999999) {
      data = (data / 1000000);
      ind = "M";
    } else if (data > 999) {
      data = (data / 1000);
      ind = "K";
    }
    var returnData = data.toFixed(1);
    return parseFloat(returnData) + ind;

  }
});




app.filter('count', function() {
  return function(value) {
    if (angular.isObject(value)) {
      return Object.keys(value).length;;
    } else if (value != null && value != "null" && value != "" && value != undefined) {
      return value.length;
    } else {
      return 0;
    }
  };
});


app.filter('age', function($filter) {
  return function(value) {
    if (value == undefined) {
      return;
    }
    var dob = $filter('date')(value, 'mm/dd/yyyy');
    var datePart = dob.split('/');
    var year = datePart[2];
    return new Date().getFullYear() - year;
  };
});

/*app.filter('filter_link', function() {
  return function(linkTypes, applicableTo) {
    debugger;
    var linkTypeFiltered = [];

    for (var i = 0; i < linkTypes.length; i++) {
      for (j = 0; j < linkTypes[i].link_combo.length; j++) {
        if (applicableTo[0].indexOf(linkTypes[i].link_combo[j][0]) > -1 && applicableTo[1].indexOf(linkTypes[i].link_combo[j][1]) > -1) {
          linkTypeFiltered.push(linkTypes[i]);
        }
      }
    }


    return linkTypeFiltered;
  }
});
*/

app.filter('filter_link', function() {
  return function(linkTypes, applicableTo) {
    var switch_list = applicableTo[2];
    var leaf2leaf_linkTypes = [];
    var gen_linkTypes = [];
    var src_tier = '';
    var dst_tier = '';
    if(undefined == switch_list) {
      src_tier = applicableTo[0];
      dst_tier = applicableTo[1];
    } else {
      switch_list.filter(function(a) {
        if(a.id == applicableTo[0]){
          src_tier = a.tier;
        }
      });
      switch_list.filter(function(a) {
        if(a.id == applicableTo[1]){
          dst_tier = a.tier;
        }
      });
    }
    
    for(var i=0;i<linkTypes.length;i++) {
      if("VPC-Member" == linkTypes[i].id || "VPC-Peer" == linkTypes[i].id) {
        leaf2leaf_linkTypes.push(linkTypes[i]);
      } else {
        gen_linkTypes.push(linkTypes[i]);
      }
    }
    if(src_tier == 'Leaf' && dst_tier == 'Leaf') {
      return leaf2leaf_linkTypes;
    }
    return gen_linkTypes;
  }
})
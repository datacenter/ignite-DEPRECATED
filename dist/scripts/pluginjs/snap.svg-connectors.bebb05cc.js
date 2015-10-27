Snap.plugin(function(Snap, Element, Paper, global) {

    var g =[];
    Paper.prototype.connection = function(obj1, obj2, line, index , hovertext) {

        if (obj1.line && obj1.from && obj1.to) {
            line = obj1;
            obj1 = line.from;
            obj2 = line.to;
        }
        var bb1 = obj1.getBBox(),
            bb2 = obj2.getBBox(),
            p = [{
                x: bb1.x + bb1.width / 2,
                y: bb1.y - 1
            }, {
                x: bb1.x + bb1.width / 2,
                y: bb1.y + bb1.height + 1
            }, {
                x: bb1.x - 1,
                y: bb1.y + bb1.height / 2
            }, {
                x: bb1.x + bb1.width + 1,
                y: bb1.y + bb1.height / 2
            }, {
                x: bb2.x + bb2.width / 2,
                y: bb2.y - 1
            }, {
                x: bb2.x + bb2.width / 2,
                y: bb2.y + bb2.height + 1
            }, {
                x: bb2.x - 1,
                y: bb2.y + bb2.height / 2
            }, {
                x: bb2.x + bb2.width + 1,
                y: bb2.y + bb2.height / 2
            }],
            d = {},
            dis = [];

        for (var i = 0; i < 4; i++) {
            for (var j = 4; j < 8; j++) {
                var dx = Math.abs(p[i].x - p[j].x),
                    dy = Math.abs(p[i].y - p[j].y);
                if ((i == j - 4) || (((i != 3 && j != 6) || p[i].x < p[j].x) && ((i != 2 && j != 7) || p[i].x > p[j].x) && ((i != 0 && j != 5) || p[i].y > p[j].y) && ((i != 1 && j != 4) || p[i].y < p[j].y))) {
                    dis.push(dx + dy);
                    d[dis[dis.length - 1]] = [i, j];
                }
            }
        }

        if (dis.length == 0) {
            var res = [0, 4];
        } else {
            res = d[Math.min.apply(Math, dis)];
        }
        var x1 = p[res[0]].x,
            y1 = p[res[0]].y,
            x4 = p[res[1]].x,
            y4 = p[res[1]].y;
        dx = Math.max(Math.abs(x1 - x4) / 2, 10);
        dy = Math.max(Math.abs(y1 - y4) / 2, 10);
        var x2 = [x1, x1, x1 - dx, x1 + dx][res[0]].toFixed(3),
            y2 = [y1 - dy, y1 + dy, y1, y1][res[0]].toFixed(3),
            x3 = [0, 0, 0, 0, x4, x4, x4 - dx, x4 + dx][res[1]].toFixed(3),
            y3 = [0, 0, 0, 0, y1 + dy, y1 - dy, y4, y4][res[1]].toFixed(3);
        //var path = "M" + x1.toFixed(3) + "," + y1.toFixed(3) + "L" + [x2, y2, x3, y3, x4.toFixed(3), y4.toFixed(3)].join();

        //Straight Path

        if(x4>x1){
            var path = "M" + x1.toFixed(3) + "," + y1.toFixed(3)+ "L" + [x4.toFixed(3), y4.toFixed(3)].join();
        }else{
            var path = "M" + x4.toFixed(3) + "," + y4.toFixed(3)+ "L" + [x1.toFixed(3), y1.toFixed(3)].join();
        }


         if (line && line.line) {
            line.line.attr({
                path: path
            });
        } else {
            var color = typeof line == "string" ? line : "yellow";

            var lineobj = {

                line: this.path(path).attr({
                    id:"path"+index,
                    x1: x1,
                    y1: y1,
                    x4: x4,
                    y4: y4,
                    stroke: color,
                    fill: "none",
                    "title": hovertext,
                    "data-toggle": "tooltip",
                    "cursor":"pointer"
                }),
                from: obj1,
                to: obj2
            };

            lineobj.line.click(function(){
                   PopEditLink(index);
            });

            lineobj.line.mouseover(function(){
                  lineobj.line.attr({
                    stroke: 'red'
                  })
            });

            lineobj.line.mouseout(function(){
                  lineobj.line.attr({
                    stroke: color
                  })
            });

            $("svg path").tooltip({
                'container': 'body',
                'placement': 'top'
            });

            return lineobj;

        }




    }

});

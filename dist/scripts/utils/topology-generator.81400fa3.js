/*Generating the layout*/

    var switchCount = 0;
    var objs = [];
    var topology = {};

    var xpos = {
        "core":[],
        "spine":[],
        "leaf":[],
        "hosts":[],
    };

    var switchDetails = [{
        "core": {
            "type": "Core",
            "x": 100,
            "y": 50,
            "w": 75,
            "h": 75,
            "img": "images/network-core.svg"
        }
    }, {
        "spine": {
            "type": "Spine",
            "x": 100,
            "y": 250,
            "w": 75,
            "h": 75,
            "img": "images/network-spine.svg"
        }
    }, {
        "leaf": {
            "type": "Leaf",
            "x": 100,
            "y": 450,
            "w": 75,
            "h": 75,
            "img": "images/network-leaf.svg"
        }
    }, {
        "host": {
            "type": "Host",
            "x": 100,
            "y": 650,
            "w": 75,
            "h": 75,
            "img": "images/network-host.svg"
        }
    }];

    var paper = "" // Snap('#topology_svg');
    var g = []; //group

    var isDragged = false;

     var createTierElement = function(count, switches, item, obj,pos) {

        //Create a group
        g[switchCount] = paper.g();

        //Set the groups coordinates
        var gx = parseInt(pos[count]);
        var gy = parseInt(obj[item].y);

        var hovertext = "Switch Name=" + switches.name + ", Switch Type="+ switches.type;

        g[switchCount].attr({
            "x": gx,
            "y": gy,
            "id": switches.id,
            "title": hovertext,
            "data-toggle": "tooltip",
            "cursor":"pointer"
        });

        $("svg g").tooltip({
        'container': 'body',
        'placement': 'right'
        });

        //add a text title and place it in the rectangle
        var switchDisplayName = switches.name;
        if (switchDisplayName.length > 12) {
          switchDisplayName = switchDisplayName.substring(0, 3) + '..' + switchDisplayName.slice(-7);
          console.log('--------NEW Switch Name----------');
          console.log(switchDisplayName);
        }
        var name = paper.text(gx + 38, gy - 6, switchDisplayName);
        name.attr({"text-anchor":"middle"})
        name.addClass('title');

        //add a rectangle below the title
        var block = paper.rect(gx, gy - 20, 75, 20, 1, 1);
        block.addClass('block');

        block.attr({
            width: (name.node.clientWidth > block.attr("width")) ? (name.node.clientWidth + 20) : block.attr("width")
        });

        //add the switch image
        var objs = paper.image(obj[item].img, gx, gy, obj[item].w, obj[item].h);

        // objs.click(function(){
        //    PopEdit(switches.id);
        // });

        objs.addClass('objs');


        //add a text type and place it below the switch image
        var type = paper.text(gx + 38, gy + 70, switches.type);
        type.attr({id:switches.name,"text-anchor":"middle"})
        type.addClass('type');


        g[switchCount].add(objs, block, name, type);


        g[switchCount].click(function(){
            PopEdit(switches.id);
        });

       // console.log('*******************');
       // console.log(g[switchCount].getBBox());

        g[switchCount].drag(dragMove,startDrag,stopDrag);

        switchCount ++;

    }

    var dragMove = function(dx, dy) {
            this.attr({
             //    transform: this.data('origTransform') + (this.data('origTransform') ? "T" : "t") + [dx, dy]
            });
    }

    var startDrag = function(){
        isDragged = true;
    }

    var stopDrag = function(){
        isDragged = false;
    }

    var connections = [];

    //Add listener for Mouse move - only needed if we can drag the group
   /* document.addEventListener('mousemove', function (e) {

            for (var i = connections.length; i--;) {
                paper.connection(connections[i]);
            }

    },false);*/

    //Create Port details - Connections




    /*****************************Create Tier Diagram **********************************************************************************************/
    var createTierDiagram = function(topology) {

        //Get Switch Positions x pos
        getSwitchPositions(topology);

        //Create Core
        if(topology.core_list!= undefined && topology.core_list.length>0){

                for (var i = 0; i < topology.core_list.length; i++) {
                    createTierElement(i, topology.core_list[i], 'core', switchDetails[0],xpos.core);
                }
        }

        //Create Spine
        if(topology.spine_list!= undefined && topology.spine_list.length>0){

                for (var i = 0; i < topology.spine_list.length; i++) {
                    createTierElement(i, topology.spine_list[i], 'spine', switchDetails[1],xpos.spine);
                }
        }

        //Create Leaf
        if(topology.leaf_list!= undefined && topology.leaf_list.length>0){
                for (var i = 0; i < topology.leaf_list.length; i++) {
                     createTierElement(i, topology.leaf_list[i], 'leaf', switchDetails[2],xpos.leaf);
                }
        }

        //Create Host
        if(topology.host_list!= undefined && topology.host_list.length>0){
                for (var i = 0; i < topology.host_list.length; i++) {
                     createTierElement(i, topology.host_list[i], 'host', switchDetails[3],xpos.hosts);
                }
        }


        createConnections(topology);
    }

    /****************************************** getswitchPosition **************************************************************/

    var getSwitchPositions = function(topology){

     xpos = {
        "core":[],
        "spine":[],
        "leaf":[],
        "hosts":[],
     };

     var svgWidth = $('#topology_svg').width();

        if(topology.core_list!= undefined && topology.core_list.length>0){
            for(var i=1; i<topology.core_list.length+1;i++){
                xpos.core.push(parseInt(svgWidth)/(topology.core_list.length +1)*i);
            }
        }

        if(topology.spine_list!= undefined && topology.spine_list.length>0){
            for(var i=1; i<topology.spine_list.length+1;i++){
                xpos.spine.push(parseInt(svgWidth)/(topology.spine_list.length +1)*i);
            }
        }

        if(topology.leaf_list!= undefined && topology.leaf_list.length>0){

            for(var i=1; i<topology.leaf_list.length+1;i++){
                xpos.leaf.push(parseInt(svgWidth)/(topology.leaf_list.length +1)*i);
            }
        }

        if(topology.host_list!= undefined && topology.host_list.length>0){
            for(var i=1; i<topology.host_list.length+1;i++){
                xpos.hosts.push(parseInt(svgWidth)/(topology.host_list.length +1)*i);
            }
        }
        console.log('xPos');
        console.log(xpos);

    }

     /****************************************** createConnections **************************************************************/
    var createConnections = function(topology) {

        console.log('******/////*******');
        console.log(topology.link_list);

         for (var i = 0; i < topology.link_list.length; i++) {

            s1 = topology.link_list[i].id_1;
            s2 = topology.link_list[i].id_2;

            p1 = topology.link_list[i].port_list_1;
            p2 = topology.link_list[i].port_list_2;

            link = topology.link_list[i].link_type;

            c1 = {};
            c2 = {};

            for (j = 0; j < g.length; j++) {
                var gp = g[j].attr("id");


                if (gp == s1) {
                    c1 = g[j];
                }
                if (gp == s2) {
                    c2 = g[j];
                }
            }

            //This is as per Link type

            var linkcolor = "blue";

            if(s1.indexOf('core')>-1){
                linkcolor = "#2256a6";
            }else if(s1.indexOf('spine')>-1){
                 linkcolor = "#27a2dc";
             }else if(s1.indexOf('leaf')>-1 && s2.indexOf('leaf')>-1){
                linkcolor = "green";
            }else if(s2.indexOf('host')>-1){
                linkcolor = "purple";
            }else{
                linkcolor = "gray";
            }

            if(link==""){
                linkcolor = "lightgray";
            }

            if (p1 != undefined && p2 != undefined) {

                var hovertext = "Link Type="+link+",  Local Port ("+s1+") ="+p1+", Remote Port ("+s2+") ="+p2;
                var connObj = paper.connection(c1, c2, linkcolor, i , hovertext);

                console.log('connObj');
                console.log(connObj);

                connections.push(connObj);

                //Get path start and end points

                var x1 = connObj.line.node.attributes.x1.nodeValue;
                var y1 = connObj.line.node.attributes.y1.nodeValue;
                var x4 = connObj.line.node.attributes.x4.nodeValue;
                var y4 = connObj.line.node.attributes.y4.nodeValue;
                var path = connObj.line.node.attributes.d.nodeValue;
                addContentToPath(x1,y1,x4,y4,path,linkcolor,p1, p2,link,i,s1,s2,hovertext);
             }


        }
    }


    var addContentToPath = function(x1,y1,x4,y4, path, linkcolor,p1, p2,link,i,s1,s2,hovertext){

        var x1 =parseInt(x1);
        var y1 =parseInt(y1);
        var x4 =parseInt(x4);
        var y4 =parseInt(y4);

        //Add a circle in the middle
        var cx = Math.floor((x1 + x4)/2.0);
        var cy = Math.floor((y1 + y4)/2.0);

        var circle = paper.circle(cx,cy,4);
        circle.click(function(){
           PopEditLink(i);
        });

        if(link==""){
            hovertext = 'Click to edit link'
        }

        circle.attr({
            fill:linkcolor,
            "title": hovertext,
            "data-toggle": "tooltip",
            "cursor":"pointer"
        });

        //add a text in the middle of the circle
        var circletext = paper.text(cx-4,cy+4,'');
        circletext.attr({
            fill: "#ffffff",
            "font-size": "14px"
        });


        if(x4>x1){
            //1 to 4
        }else{

            var s1x = s1;
            var s2x = s2;
            var p1x = p1;
            var p2x = p2;

            s1 = s2x;
            s2 = s1x;
            p1 = p2x;
            p2 = p1x;
        }

        pathLength = Snap.path.getTotalLength(path);

        //console.log('*************Before Map****************')
        //console.log(p1);
        //console.log(p2);


        var charPort1 = "";
        var charPort2 = "";
        p1 = p1.map(function(e) {
            var numAt = e.search(/\d/,'');
            charPort1 = e.substring(0,numAt)
            var removeChar = e.replace(charPort1,'');
            return removeChar;
        });

        p2 = p2.map(function(e) {
            var numAt = e.search(/\d/,'');
            charPort2 = e.substring(0,numAt)
            var removeChar = e.replace(charPort2,'');
            return removeChar;
        });


        //console.log('-------------After map---------------------')
        //console.log(p1);
        //console.log(p2);

        if(p1.length>1){
            p1 = charPort1 +""+ p1[0] + '-' + p1[p1.length-1];
        }else{
            p1 = charPort1 +"" + p1[0];
        }

        if(p2.length>1){
            p2 = charPort2 +""+ p2[0] + '-' + p2[p2.length-1];
        }else{
            p2 = charPort2 +"" + p2[0];
        }

        //console.log('--------------Final text--------------------')
        //console.log(p1);
        //console.log(p2);

        //Add port details
        var portText1 = paper.text(10, 0, p1.toString());
        portText1.attr({
            fill:linkcolor,
            textpath:path,
            id:"port-"+s1
        });
        portText1.addClass('port');

        var portText2 = paper.text(0, 0, p2.toString());
        portText2.attr({
            fill:linkcolor,
            textpath:path,
            id:"port-"+s2
        });

        // console.log('-------------------------------------------');
        // console.log(portText2.node);
        // console.log('*******************************************');
        // console.log(portText2.node.getBoundingClientRect());

        // portText2.textPath.attr({'startOffset':pathLength - (portText2.node.clientWidth/1.25)}); //80
        portText2.textPath.attr({'startOffset':pathLength - 70}); //80
        portText2.addClass('port');

        var g = paper.g();
        g.add(circle,circletext,portText1,portText2);

         $("svg circle").tooltip({
        'container': 'body',
        'placement': 'right'
        });

    }

    var panTopology = null;
    var setTopologyData = function(topology){

        topology = topology.topology_json;

        var sWidth = $('#topology_svg').width();

        if(topology.leaf_list.length>10){
            $('#topology_svg').width(topology.leaf_list.length*100+"px");
        }

        paper = Snap('#topology_svg');


        console.log('Setting Topology Data');
        console.log(topology);
     //   GroupTierElements(topology);

         createTierDiagram(topology);



          panTopology = svgPanZoom('#topology_svg', {
          controlIconsEnabled: true,
          fit: true,
          zoomScaleSensitivity: 0.4,
          contain: true,
          beforePan: function(){
                return !isDragged;
          },
          center: true
        });

        // Pan to rendered point i.e center of svg
        // var svgCenter = parseInt($('#topology_svg').width()/6);
        // console.log('svgCenter='+svgCenter)

        //panTopology.pan({x: svgCenter, y: 10})
        //panTopology.zoomAtPoint(2, {x: 800, y: 300});
        //panTopology.resetZoom()

        //panTopology.updateBBox(); // Update viewport bounding box
        //panTopology.fit(); // fit works as expected

    }


    var itemID = 0;
    var itemLinkID = 0;


    var doReload = function(topology){
        //Clear the group array and reset the switch Count;
        g = [];
        switchCount = 0;

        svgPanZoom('#topology_svg').destroy();
        panTopology = null;
        clearPaper();
        closePopEdit();
        setTopologyData(topology);
        console.log(topology);
    }

    var saveReloadTopology = function(topology){

        svgPanZoom('#topology_svg').destroy();
        panTopology = null;
        clearPaper();

        setTopologyData(topology);
        $('#popEdit').hide();
        $('#popEditLink').hide();
    }


    var closePopEdit = function(){
        $('#popEdit').hide();
        closePopEditLink();
    }

    var clearPaper = function(){
        if(paper!=""){
            paper.clear();
        }
    }


   var PopEdit = function (id){
        //console.log("popEdit_Item_"+id);
        closePopEdit();

         $('#popEdit_Item_'+itemID).hide();
         $('#popEditLink_Item_'+itemLinkID).hide();
        // $('#popEdit').css({left:parseInt(posX),top:parseInt(posY)});
         $('#popEdit').show();
         $('#popEdit_Item_'+id).show();
         itemID = id;
    }


    var PopEditLink = function (id){
        closePopEdit();
        $('#popEdit_Item'+itemID).hide();
        $('#popEditLink_Item'+itemLinkID).hide();
      //  $('#popEdit').css({left:parseInt(posX),top:parseInt(posY)});

        $('#popEditLink').show();
        $('#popEditLink_Item'+id).show();

        //Write code to scroll to anchor location
        //$('#listItem_'+id).offset().top;
        $('#listItem_'+id).addClass('active');
        itemLinkID = id;
    }

    var closePopEditLink = function(){
        $('#popEditLink').hide();
        $('#listItem_'+itemLinkID).removeClass('active');
    }

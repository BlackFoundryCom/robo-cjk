
// Copyright 2019 Black Foundry.

// This file is part of Robo-CJK.

// Robo-CJK is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

// Robo-CJK is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.

// You should have received a copy of the GNU General Public License
// along with Robo-CJK.  If not, see <https://www.gnu.org/licenses/>.


var args = process.argv.slice(2);
console.log(args)

const fs = require('fs');
const Viz = require('viz.js');
const { Module, render } = require('viz.js/full.render.js');


let viz = new Viz({ Module, render });

var diagramFile = 'documentation/' + args
var savepath = "documentation/"+args[0].slice(0, -3)+"svg"

var dot = fs.readFile(diagramFile, 'utf-8', (err, data) => {
  if (err) throw err;
  console.log(data);
  viz.renderString(data, {engine: "dot"})
  .then(result => {
    // console.log(result);
    fs.writeFile(savepath, result, (err) => {
      if (err) throw err;
      console.log('The file has been saved!');
    });

  })
  .catch(error => {
    console.error(error);
  });
});



// var graphviz = require('graphviz');

// var g = graphviz.digraph("RoboCJK");
// g.set("rankdir", "TB")
// g.setNodeAttribut("shape", "record")
// g.setNodeAttribut("fontname", "Courier")

// var n1 = g.addNode( "Hello", {"color" : "blue"} );
// n1.set( "style", "filled" );

// // Add node (ID: World)
// g.addNode( "World" );

// // Add edge between the two nodes
// var e = g.addEdge( n1, "World" );
// e.set( "color", "red" );

// // Print the dot script
// console.log( g.to_dot() );

// // Set GraphViz path (if not in your path)
// // Generate a PNG output
// g.output( "svg", "documentation/Diagram.svg" );


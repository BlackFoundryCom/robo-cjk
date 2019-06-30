const fs = require('fs');
const Viz = require('viz.js');
const { Module, render } = require('viz.js/full.render.js');


let viz = new Viz({ Module, render });

var diagramFile = 'documentation/dot.txt'

var dot = fs.readFile(diagramFile, 'utf-8', (err, data) => {
  if (err) throw err;
  console.log(data);
  viz.renderString(data, {engine: "dot"})
  .then(result => {
    console.log(result);
    fs.writeFile("documentation/Diagram.svg", result, (err) => {
      if (err) throw err;
      console.log('The file has been saved!');
    });

  })
  .catch(error => {
    // Possibly display the error
    console.error(error);
  });
});








// function buildHtml(req) {
//   var header = '';
//   var body = '';

//   // concatenate header string
//   // concatenate body string

//   return '<!DOCTYPE html>'
//        + '<html><head>' + header + '</head><body>' + body + '</body></html>';
// };

// var fileName = 'mermaidDoc/index.html';
// var stream = fs.createWriteStream(fileName);

// stream.once('open', function(fd) {
//   var html = buildHtml();
//   stream.end(html);
// });
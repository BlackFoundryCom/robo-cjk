const fs = require('fs');
const mermaidAPI = require('mermaid');

mermaidAPI.initialize({startOnLoad: false});


fs.open('Diagram.md', 'r', (err, fd) => {
  if (err) throw err;

  mermaidAPI.render('theDiagram', fd, function(svgCode) {
        fs.writeFile("Diagram.svg", new Buffer(svgCode))
    });

  fs.close(fd, (err) => {
    if (err) throw err;
  });
});

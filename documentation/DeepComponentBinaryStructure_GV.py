import graphviz as gv 

dot = gv.Graph('Deep Component Binary Structure', engine='dot') #fdp#circo
dot.attr(rankdir='BL')

dot.attr('node', shape='cds')

dot.node('GLYF', 'GLYF', shape='circle', style='filled', color="cyan")
dot.node('GVAR', 'GVAR', shape='circle', style='filled', color="pink")
dot.node('FVAR', 'FVAR', shape='circle', style='filled', color="yellow")

dot.node('ae', 'Atomic Element', shape='cylinder', style='filled', fillcolor="cyan", color="black")
dot.node('dc', 'Deep Component', shape='cylinder', style='filled', fillcolor="cyan", color="black")
dot.node('cg', 'Character Glyph', shape='cylinder', style='filled', fillcolor="cyan", color="black")

dot.edge('ae', 'GLYF')
dot.edge('dc', 'GLYF')
dot.edge('cg', 'GLYF')

dot.node('aelg', 'n <contour>', style='filled', color="cyan")
dot.node('dcog', 'n <atomicElement>', style='filled', color="cyan")
dot.node('cglg', 'n <deepComponent>', style='filled', color="cyan")

dot.edge('ae', 'aelg')
dot.edge('dc', 'dcog')
dot.edge('cg', 'cglg')

dot.node('aelv', ' <delta>', style='filled', color="pink")
dot.node('dcov', ' <deltaAtomicElement>', style='filled', color="pink")
dot.node('cglv', ' <deltaDeepComponent>', style='filled', color="pink")

dot.edge('aelv', 'aelg')
dot.edge('dcov', 'dcog')
dot.edge('cglv', 'cglg')

dot.edge('aelv', 'GVAR')
dot.edge('dcov', 'GVAR')
dot.edge('cglv', 'GVAR')

dot.node('faev', ' <AxisAtomicElement>', style='filled', color="yellow")
dot.node('fdcv', ' <AxisDeepComponent>', style='filled', color="yellow")
dot.node('fcgv', ' <Axis>', style='filled', color="yellow")

dot.edge('aelv', 'faev')
dot.edge('dcov', 'fdcv')
dot.edge('cglv', 'fcgv')

dot.edge('FVAR', 'faev')
dot.edge('FVAR', 'fdcv')
dot.edge('FVAR', 'fcgv')

dot.edge('cglg', 'fdcv')
dot.edge('dcog', 'faev')


print(dot.source)
dot.render('DeepComponentBinaryStructure.gv', view=True, format='svg')
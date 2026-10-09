"""Guarded adapters from reviewed foundation commit 0c980b0; no geometry edits."""

def adapt_cpu(source):
    replacements = {
        "'use strict';": "'use strict'; let publicAvailability='loading';",
        'const index=M.validate(catalog,taxonomy), progress=M.projectProgress(index,ledger,{publicOnly:true});':
        'const index=M.validate(catalog,taxonomy), baseProgress=M.projectProgress(index,ledger,{publicOnly:true}); let progress=baseProgress;',
        'const V=LeetCodeVisualState,compiled=V.compile(index),projection=V.project(compiled,progress);let coverage;':
        'const V=LeetCodeVisualState,compiled=V.compile(index);let projection=V.project(compiled,progress),coverage;',
        'function installSummary(){': 'function installSummaryOriginal(){',
        'function updateVisual(){': 'function updateVisualOriginal(){',
        'function inspect(){': 'function inspectOriginal(){',
        'window.LeetCodeAtlas={state:': 'window.LeetCodeAtlas={setPublicProgress,setPublicProgressStatus,state:',
        "document.body.dataset.ready='true';": "document.body.dataset.ready='true';window.dispatchEvent(new Event('atlas-ready'));",
    }
    for old, new in replacements.items():
        if source.count(old) != 1:
            raise ValueError('CPU source changed; review integration hook: ' + old)
        source = source.replace(old, new)
    hook = '''
function publicKnown(){return !['loading','unavailable'].includes(publicAvailability);}
function maskPublicUnknown(){
 if(publicKnown())return;
 const summary=$('global-progress');
 if(summary){summary.querySelector('.progress-count').textContent='— / '+catalog.problems.length.toLocaleString('en-US')+' solved · unavailable';summary.querySelector('strong').textContent='Unknown';}
 document.querySelectorAll('.progress-meter').forEach(e=>{e.hidden=true;e.style.display='none';e.removeAttribute('aria-valuenow');});
 const problem=document.querySelector('.progress-state');if(problem)problem.textContent='Public progress unavailable';
 document.querySelectorAll('.coverage-count').forEach(e=>e.textContent='Public progress unavailable');
}
function installSummary(){
 installSummaryOriginal();
 $('catalog-legend').append($('difficulty-distribution'));
 for(const [name,ids] of compiled.difficulties){
  const legend=[...document.querySelectorAll('.difficulty-legend')].find(e=>e.textContent.startsWith(name+' '));
  if(legend){const count=el('span',publicKnown()?V.summary(ids,projection.solved).solved+' solved':'— solved','difficulty-solved');count.dataset.difficulty=name;legend.append(count);}
 }
 maskPublicUnknown();
}
function updateVisual(){updateVisualOriginal();if(!publicKnown())visual.coverage=new Map();maskPublicUnknown();}
function inspect(){inspectOriginal();maskPublicUnknown();}
function refreshPublicPresentation(){
 $('global-progress').remove();$('difficulty-distribution').remove();installSummary();
 updateVisual();renderResults();inspect();requestPaint();
}
function setPublicProgressStatus(status){
 if(!['loading','unavailable','stale','published'].includes(status))throw Error('Invalid public availability');
 publicAvailability=status;document.body.dataset.publicProgress=status;refreshPublicPresentation();
}
function setPublicProgress(value){
 progress=MyAtlasReadOnlyProgress.project(baseProgress,value);
 projection=V.project(compiled,progress);coverage=V.presentation(L,projection);relationKey=null;
 refreshPublicPresentation();return progress.uniqueSolved;
}
'''
    return source.replace('window.LeetCodeAtlas={', hook + '\nwindow.LeetCodeAtlas={')

def adapt_top_ui(html):
    """Reparent existing controls into normal-flow toolbars; keep IDs and handlers."""
    edits = {
        '<div id="filter-context"><p id="atlas-context"': '<div id="filter-context"><div id="catalog-legend"><p id="atlas-context"',
        '</p><span id="result-count"': '</p></div><span id="result-count"',
        '<section id="canvas-container" aria-label="LeetCode problem floorplan">\n<div class="map-controls">':
        '<div id="map-toolbar" role="toolbar" aria-label="Map navigation"><div class="map-controls"><div class="map-navigation">',
        '<button id="zoom-out"': '</div><div class="map-zoom" role="group" aria-label="Zoom"><button id="zoom-out"',
        '<button id="zoom-in" aria-label="Zoom in">+</button></div>': '<button id="zoom-in" aria-label="Zoom in">+</button></div></div>',
        '<nav id="overview-guide" aria-label="LeetCode algorithm families"></nav>':
        '<button id="inspector-toggle" aria-controls="inspector-drawer" aria-expanded="false">Inspect ‹</button></div>\n<nav id="overview-guide" aria-label="LeetCode algorithm families"></nav>\n<div id="map-stage"><section id="canvas-container" aria-label="LeetCode problem floorplan">',
        '<button id="inspector-toggle" aria-controls="inspector-drawer" aria-expanded="false">Inspect ‹</button>\n\n': '',
        '</div></div>\n</main>': '</div></div></div>\n</main>',
    }
    for old, new in edits.items():
        if html.count(old) != 1:
            raise ValueError('Accepted top UI changed; review markup: ' + old)
        html = html.replace(old, new)
    return html

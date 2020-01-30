import {getFlameGraphDictByNum} from "./profiling/flamegraphs.js";
import {getGraphDictByNum, drawGraph} from "./monitoring/timeseries.js";

import {graphsContainerId} from "../index.js";
import {graphs_dict} from "./monitoring/timeseries.js";


const graphsIdBase = "graph_";
export function getGraphNumFromID(ID) {
    "use strict";
    return ID.split("_")[1];
}

export function getGraphID(graph_num) {
    "use strict";
    return graphsIdBase + graph_num;
}

export function removeGraphByNumber(graph_type, graph_number) {
    "use strict";
    let graphsContainer = document.getElementById(graphsContainerId);
    let graphsContainers = graphsContainer.children;
    let graphID = getGraphID(graph_number);

    for (let graph of graphsContainers) {
        if (graph.id.split("_")[2] === graph_number && graph_type === graph.id.split("_")[1]) {
            graphsContainer.removeChild(graph);
            delete graphs_dict[graphID];
            break
        }
    }
}

export function triggerResize(graphID, graphX, graphY) {
    "use strict";
    let graph_number = getGraphNumFromID(graphID);
    let resizableContainer;
    if (graphID.startsWith("flamegraph_")) {
        let flamegraph_info = getFlameGraphDictByNum(graph_number);
        changeFlamegraphSize(graph_number, graphX, graphY);
        drawFlameGraph(flamegraph_info["data"], graphID, false);
        resizableContainer = document.getElementById("containerResizableFlamegraph_" + graphID)
    }else if (graphID.startsWith(graphsIdBase)) {
        let graph_info = getGraphDictByNum(graph_number);
        changeImageSize(graph_number, graphX, graphY);
        drawGraph(graph_info["data"], graphID, false);
        resizableContainer = document.getElementById("containerResizable_" + graphID)
    }
    resizableContainer.style = "overflow:auto;"
}

function changeImageSize(graph_number, graphX, graphY) {
    let graph_info = getGraphDictByNum(graph_number);
    graph_info["sizeX"] = graphX;
    graph_info["sizeY"] = graphY
}
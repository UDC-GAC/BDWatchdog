import {divFormsIdBase} from "./monitorings.js";
import {createCORSRequest, graphsContainerId, timeConverter} from "../../index.js";
import {getGraphNumFromID, getGraphID} from "../graphs.js";
import {getFormFromDiv} from "../forms.js";
import {nv} from "./dynamicChartD3_3v.js";

let graph_counter = 0;
export let graphs_dict = {};

let defaultURL = "http://opentsdb:4242";

export let defaultStartDate = "2017/02/12-17:28:21"; // FIXME better set value to now minus five minutes
export let defaultEndDate = "2017/02/12-17:32:06"; // FIXME better set value to now

export let min_range = 0;
export let max_range = 100;
export let applyScale = false;

export let x_time_reduction_factor = 1;

export const defaultXSize = "600";
export const defaultYSize = "300";

let strokeColors = ["blue", "red", "green", "orange", "purple", "steelblue"];

let downsamplingMap = {
    "minimal": "1s-avg",
    "lowest": "5s-avg",
    "low": "20s-avg",
    "medium": "60s-avg",
    "high": "2m-avg",
    "very_high": "10m-avg",
    "highest": "1h-avg"
};

//##### AUXILIAR ######
export function createJson(start_date, end_date, metrics, graph_number, downsampling) {
    "use strict";
    let final_dict = {};
    final_dict.start = start_date;
    final_dict.end = end_date;

    if (downsampling === undefined) {
        if (graph_number === -1) {
            downsampling = "auto";
        } else {
            downsampling = getDownsampling(graph_number);
        }
    }

    if (downsampling === "auto") {
        // Change the date string format so that Firefox doesn't complain
        // 2019/12/17-02:34:33  -> should be -> 2019-12-17T02:34:33
        end_date = end_date.replace("-", "T");
        // Do 2 replaces to avoid using pattern matching, which requires the character / in sed style (e.g., /blue/g)
        end_date = end_date.replace("/", "-");
        end_date = end_date.replace("/", "-");
        start_date = start_date.replace("-", "T");
        start_date = start_date.replace("/", "-");
        start_date = start_date.replace("/", "-");
        let end_date_seconds = new Date(end_date).getTime();
        let start_date_seconds = new Date(start_date).getTime();
        let timeDiff = (end_date_seconds - start_date_seconds) / 1000;

        //intervals range using hours
        if (timeDiff <= 3600) {
            downsampling = downsamplingMap.lowest;
        } else if (timeDiff <= 2 * 3600) {
            downsampling = downsamplingMap.low;
        } else if (timeDiff <= 4 * 3600) {
            downsampling = downsamplingMap.medium;
        } else if (timeDiff <= 8 * 3600) {
            downsampling = downsamplingMap.high;
        } else if (timeDiff <= 24 * 3600) {
            downsampling = downsamplingMap.very_high;
        } else if (timeDiff > 24 * 3600) {
            downsampling = downsamplingMap.highest;
        } else {
            downsampling = downsamplingMap.medium;
        }
    }

    let queries = [];
    for (let m of metrics) {
        let aggregator = m["aggregator"];
        let metric = m["metric"];
        let tags_dict = {};
        let tag;
        let value;
        let tags = m["tags"];
        for (let t of tags) {
            tag = t.split("=")[0];
            value = t.split("=")[1];
            tags_dict[tag] = value
        }
        let query = {};
        query["aggregator"] = aggregator;
        query["metric"] = metric;
        query["tags"] = tags_dict;
        query["downsample"] = downsampling;
        queries.push(query)
    }

    final_dict["queries"] = queries;
    return final_dict
}

function encodeTags(tags) {
    "use strict";
    return "%7B" + tags.toString() + "%7D"
}

function getGraphDictById(graphID) {
    "use strict";
    return graphs_dict[graphID]
}

export function getGraphDictByNum(graph_number) {
    "use strict";
    let graphID = getGraphID(graph_number);
    return graphs_dict[graphID]
}

function getDownsampling(form_number) {
    "use strict";
    let formID = divFormsIdBase + form_number;
    let form = document.getElementById(formID);
    let downsamplingDiv = form.getElementsByClassName("downsampling-div")[0];
    let dropdown = downsamplingDiv.children[1];
    return dropdown.options[dropdown.selectedIndex].value
}

//######################

//##### DRAWING ######
function addLoaderToGraph(graphID) {
    "use strict";
    let graph_container = document.getElementById("containerResizable_" + graphID);
    let loader = document.createElement("div");
    loader.classList.add("loader");
    graph_container.appendChild(loader)
}

function removeLoaderFromGraph(graphID) {
    "use strict";
    let graph_container = document.getElementById("containerResizable_" + graphID);
    let children = graph_container.childNodes;
    for (let child of children) {
        if (child.tagName === "DIV" && child.classList.contains("loader")) {
            graph_container.removeChild(child)
        }
    }
}

function addNoDataAvailableToGraph(graphID) {
    "use strict";
    let container = document.getElementById("container_" + graphID);
    let noDataLabel = document.createElement("text");
    noDataLabel.insertAdjacentHTML("afterbegin", "NO DATA AVAILABLE");
    container.appendChild(noDataLabel)
}

function removeNoDataAvailableFromGraph(graphID) {
    "use strict";
    let container = document.getElementById("container_" + graphID);
    let children = container.childNodes;
    for (let child of children) {
        if (child.tagName === "TEXT") {
            container.removeChild(child)
        }
    }
}

export function reDrawGraphByNumber(graph_number) {
    "use strict";
    let graph_info = getGraphDictByNum(graph_number);
    let start_date = graph_info["start_date"];
    let end_date = graph_info["end_date"];
    let metrics = graph_info["metrics"];
    let graphID = getGraphID(graph_number);

    let svg = d3.select("#" + graphID);
    if (svg.empty()) {
        //Create new graph
        d3.select("#" + graphsContainerId)
            .append("div")
            .attr("id", "container_" + graphID)
            .attr("class", "resize-container")
            .append("div")
            .attr("class", "resize-drag")
            .attr("id", "containerResizable_" + graphID)
            .append("svg")
            .attr("id", graphID)
            .attr("width", 0)
            .attr("height", 0)

    } else {
        //Empty the graph and remove loader and "no data warning", if any
        svg.selectAll("g").remove();
        svg.selectAll("text").remove();
        removeLoaderFromGraph(graphID);
        removeNoDataAvailableFromGraph(graphID)
    }

    addLoaderToGraph(graphID);

    //Define the callback function to draw data after it has been retrieved
    let callback = function (response, graphID) {
        graph_info["data"] = parseResponseMetricsData(response);
        drawGraph(graph_info["data"], graphID, true)
    };

    let callback_error = function (response, graphID) {
        graph_info["data"] = {};
        graph_info["data"]["points"] = [];
        drawGraph(graph_info["data"], graphID, true)
    };

    getGraphData(createJson(start_date, end_date, metrics, graph_number), graphID, callback, callback_error)
}

export function parseResponseMetricsData(allMetricsData) {
    "use strict";
    let metrics;
    let timeDiff_loop;
    let single_array = [];
    let points_array = [];

    //create labels array
    let labels_array = [];
    for (let metricData of allMetricsData) {
        let tags_string_array = [];
        let tags = Object.keys(metricData["tags"]);
        for (let tag of tags) {
            tags_string_array.push(tag + ":" + metricData["tags"][tag])
        }
        let tags_string = tags_string_array.join(",");
        labels_array.push(metricData["metric"] + ";" + tags_string)
    }

    //Look for the highest and lowest timestamp
    let lowestTime = 9007199254740992; //Max int in Javascript
    let highestTime = 0;
    for (let metricData of allMetricsData) {
        metrics = metricData["dps"];
        let key = Object.keys(metrics)[0];
        let parsedKey = parseInt(key);
        if (!isNaN(parsedKey)) {
            lowestTime = Math.min(lowestTime, parseInt(key))
        }
    }

    for (let metricData of allMetricsData) {
        metrics = metricData["dps"];
        for (let key in metrics) {
            if (metrics.hasOwnProperty(key)) {
                timeDiff_loop = key - lowestTime;
                single_array.push({
                    value: metrics[key],
                    time: timeDiff_loop
                });
                highestTime = Math.max(highestTime, parseInt(key))
            }
        }
        points_array.push(single_array);
        single_array = []
    }

    let allMetricsValues = {};
    allMetricsValues["points"] = points_array;
    allMetricsValues["labels"] = labels_array;
    allMetricsValues["real_start"] = lowestTime;
    allMetricsValues["real_end"] = highestTime;

    return allMetricsValues
}

function translateMetric(metric) {
    let translated_metric = metric;

    //CPU
    translated_metric = translated_metric.replace("proc.cpu.user", "User CPU");
    translated_metric = translated_metric.replace("proc.cpu.kernel", "Kernel CPU");
    translated_metric = translated_metric.replace("structure.cpu.usage", "CPU Used");
    translated_metric = translated_metric.replace("structure.cpu.current", "CPU Allocated");
    translated_metric = translated_metric.replace("structure.cpu.min", "CPU Min");
    translated_metric = translated_metric.replace("structure.cpu.max", "CPU Max");
    translated_metric = translated_metric.replace("limit.cpu.upper", "CPU upper lim");
    translated_metric = translated_metric.replace("limit.cpu.lower", "CPU lower lim");

    //ENERGY
    translated_metric = translated_metric.replace("structure.energy.max", "Energy Allowed");
    translated_metric = translated_metric.replace("structure.energy.min", "Min Energy given");
    translated_metric = translated_metric.replace("structure.energy.usage", "Energy Used");

    //MEM
    translated_metric = translated_metric.replace("proc.mem.resident", "Resident MEM");
    translated_metric = translated_metric.replace("proc.mem.virtual", "Virtual MEM");
    translated_metric = translated_metric.replace("proc.mem.swap", "Swap MEM");

    //DISK
    translated_metric = translated_metric.replace("proc.disk.writes.mb", "Writes Disk");
    translated_metric = translated_metric.replace("proc.disk.reads.mb", "Reads Disk");

    //NET
    translated_metric = translated_metric.replace("proc.net.tcp.in", "In TCP Network");
    translated_metric = translated_metric.replace("proc.net.tcp.out", "Out TCP Network");

    return translated_metric
}

function translateCommand(command) {
    let translated_command = command;
    translated_command = translated_command.replace("CoarseGrainedExecutorBackend", "Spark Executor");
    translated_command = translated_command.replace("YarnChild", "Yarn Containers");
    return translated_command
}

function translateHost(host) {
    let translated_host = host;
    return translated_host
}

function translateLabels(labels) {
    "use strict";
    let translatedLabels = [];

    for (let j = 0; j < labels.length; j++) {
        let label = labels[j];

        let splits = label.split(";");

        let translated_metric = translateMetric(splits[0]);

        let translated_command = "";
        let translated_host = "";
        let structure = ""
        for (let z = 1; z < splits.length; z++) {
            let split = splits[z];
            if (split.includes("command")) {
                translated_command = translateCommand(split)
            } else {
                translated_command = "command:ALL"
            }
            if (split.includes("host")) {
                translated_host = translateHost(split)
            } else {
                translated_host = "host:ALL"
            }
            if (split.includes("structure")) {
                structure = split
            }
        }

        let translated_label = "";
        if (label.includes("structure")){
            translated_label = translated_metric + " , " + translated_command + " , " + structure;
        }else {
            translated_label = translated_metric + " , " + translated_command + " , " + translated_host;
        }

        translatedLabels.push(translated_label)
    }
    return translatedLabels
}

function translateYGraphLabel(firstMetric) {
    "use strict";
    let label = "UNKNOWN";


    if (firstMetric.startsWith("proc.cpu.energy") || firstMetric.startsWith("sys.cpu.energy")
        || firstMetric.startsWith("structure.energy.max") || firstMetric.startsWith("structure.energy.usage")) {
        label = "Energy (J)"
    } else if (firstMetric.startsWith("proc.cpu") || firstMetric.startsWith("sys.cpu")
        || firstMetric.startsWith("structure.cpu.current") || firstMetric.startsWith("structure.cpu.usage")) {
        label = "CPU (%)"
    } else if (firstMetric.startsWith("proc.mem") || firstMetric.startsWith("sys.mem")) {
        label = "Memory (MiB)"
    } else if (firstMetric.startsWith("proc.disk") || firstMetric.startsWith("sys.disk")) {
        label = "Disk bandwidth (MiB/s)"
    } else if (firstMetric.startsWith("proc.net") || firstMetric.startsWith("sys.net")) {
        label = "Network bandwidth (Mbps)"
    } else if (firstMetric.startsWith("sys.swap.free")) {
        label = "Free swap (MB)"
    }
    //Override for system usage
    if (firstMetric.startsWith("sys.cpu.usage")
        || firstMetric.startsWith("sys.mem.usage")
        || firstMetric.startsWith("sys.disk.usage")
        || firstMetric.startsWith("sys.net.usage")) {
        label = "% Usage over 100 (full use of resource)"
    }
    return label
}

function getTimeLabel(start_time, end_time) {
    "use strict";
    let time_label_tail = timeConverter(start_time) + " to " + timeConverter(end_time);
    let time_label = "Time (s) from " + time_label_tail;

    let time_diff = end_time - start_time;
    x_time_reduction_factor = 1; //Global letiable

    if (time_diff > 3600) {
        //Greater than an hour
        x_time_reduction_factor = 60;
        time_label = "Time (m) from " + time_label_tail
    } else if (time_diff > 216000) {
        //Greater than an 60 hours
        x_time_reduction_factor = 3600;
        time_label = "Time (h) from " + time_label_tail
    } else if (time_diff > 12960000) {
        //Greater than an 3609 hours (150 days)
        x_time_reduction_factor = 216000;
        time_label = "Time (d) from " + time_label_tail
    }

    return time_label
}


export function drawGraph(parsedData, graphID, dataHasChanged) {
    "use strict";

    let graph_number = getGraphNumFromID(graphID);
    let graph_info = getGraphDictByNum(graph_number);

    let margin = {top: 0, right: 0, bottom: 0, left: 0};
    let width = +graph_info["sizeX"] - margin.left - margin.right;
    let height = +graph_info["sizeY"] - margin.top - margin.bottom;

    let svg = d3.select("#" + graphID);
    if (svg.empty()) {
        //Create new graph
        svg = d3.select("#" + graphsContainerId)
            .append("div")
            .attr("id", "container_" + graphID)
            .attr("class", "resize-container")
            .append("div")
            .attr("class", "resize-drag")
            .attr("id", "containerResizable_" + graphID)
            .append("svg")
            .attr("id", graphID)
            .attr("width", width)
            .attr("height", height)
    } else {
        svg.selectAll("g").remove();
        svg.selectAll("text").remove()
    }

    removeNoDataAvailableFromGraph(graphID);
    removeLoaderFromGraph(graphID);

    if (parsedData["points"].length === 0) {
        addNoDataAvailableToGraph(graphID);
        return
    }

    let points;
    let labels_array;
    let translatedLabels;
    if (dataHasChanged) {
        let allMetricsValues = parsedData["points"];
        labels_array = parsedData["labels"];
        translatedLabels = translateLabels(labels_array);
        points = [];
        let valuesArr = [];
        for (let i = 0; i < allMetricsValues.length; i++) {
            let metrics = allMetricsValues[i];
            valuesArr = [];
            for (let j = 0; j < metrics.length; j++) {
                valuesArr.push([metrics[j].time, metrics[j].value])
            }
            points.push({data: valuesArr, label: translatedLabels[i]})
        }
        graph_info["points"] = points;
        graph_info["labels"] = labels_array;
        graph_info["real_start"] = parsedData["real_start"];
        graph_info["real_end"] = parsedData["real_end"]
    } else {
        points = graph_info["points"];
        labels_array = graph_info["labels"];
        translatedLabels = translateLabels(labels_array)
    }

    let scale_form = getFormFromDiv(document.getElementById(divFormsIdBase + getGraphNumFromID(graphID)));
    applyScale = scale_form.elements.scaleY.checked;
    if (scale_form && applyScale) {
        min_range = scale_form.elements.min_y.value;
        max_range = scale_form.elements.max_y.value
    }

    let yLabel = translateYGraphLabel(labels_array[0]);
    let timeLabel = getTimeLabel(graph_info["real_start"], graph_info["real_end"]);

    let chart = nv.models.lineWithLegend()
        .xAxis.label(timeLabel)
        .width(width)
        .height(height)
        .yAxis.label(yLabel);

    svg.datum(points);
    svg.transition().duration(500)
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .call(chart)
}

//######################

//####### ADD GRAPH #######

export function increase_graph_counter() {
    graph_counter = graph_counter + 1
}

export function decrease_graph_counter() {
    graph_counter = graph_counter - 1
}

export function addGraph(metrics) {
    "use strict";
    //Generate the ID string of the graph
    let graphID = getGraphID(graph_counter);

    //Store all the graph data and metadata
    graphs_dict[graphID] = {};
    let graph_info = graphs_dict[graphID];
    graph_info["start_date"] = defaultStartDate;
    graph_info["end_date"] = defaultEndDate;
    graph_info["metrics"] = metrics;
    graph_info["sizeX"] = defaultXSize;
    graph_info["sizeY"] = defaultYSize;
    graph_info["data"] = {};
    graph_info["data"]["points"] = [];
    graph_info["data"]["labels"] = [];

    //Increment the counter of graphs displayed
    increase_graph_counter()
}

//######################

//######## MODIFY ###########
export function changeGraphValues(graph_number, metrics, start_date, end_date) {
    "use strict";
    let graph_info = getGraphDictByNum(graph_number);
    graph_info["start_date"] = start_date;
    graph_info["end_date"] = end_date;
    graph_info["metrics"] = metrics
}

//######################

//######## AJAX AND HTTP CALLS ############
export function getGraphData(json, graphID, callback, callback_error) {
    "use strict";
    let url = document.getElementById("config_form").elements.endpoint_OpenTSDB.value;
    if (url === "undefined" || url === "") {
        url = defaultURL
    }

    let xhr = createCORSRequest("POST", url + "/api/query");
    if (!xhr) {
        throw new Error("CORS not supported")
    }
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.setRequestHeader("Accept", "application/json");

    let response;
    xhr.onload = function () {
        if (xhr.status === 200) {
            response = JSON.parse(xhr.responseText);
            let graph_info = graphs_dict[graphID];
            callback(response, graphID)
        } else {
            response = JSON.parse(xhr.responseText);
            //alert("Error getting graph data")
            callback_error(response, graphID)
        }
    };

    xhr.onerror = function () {
        //alert("Woops, there was an error making the request.")
        callback_error(response, graphID)
    };

    xhr.send(JSON.stringify(json))
}

//####################################

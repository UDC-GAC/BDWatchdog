import {timeConverter} from "../../index.js";
import {getMongoURLfromUI, sendCORSrequest} from "./shared.js";

let deleted_experiments = [];

export function getExperimentsFromMongo(username) {
    "use strict";
    let endpoint = getMongoURLfromUI();
    let mongo_REST_endpoint = endpoint + "/experiments?where={%22username%22:%22" + username + "%22}";
    getExperimentsFromMongoPaginated(mongo_REST_endpoint, true)

}

function getExperimentsFromMongoPaginated(mongo_REST_endpoint, remove_previous) {
    let headers = [{"header": "Accept", "value": "application/json"}];
    sendCORSrequest("GET", mongo_REST_endpoint, headers, 200, function (response) {
        populateExperimentsDropdown(response, remove_previous);
        if (response._meta["page"] * response["_meta"]["max_results"] < response["_meta"]["total"]) {
            getExperimentsFromMongoPaginated(getMongoURLfromUI() + "/" + response["_links"]["next"]["href"], false);
        }
    }, "Error getting experiments");
}

export function getExperimentTimes() {
    "use strict";
    let experiments_form = document.getElementById("experiment_picker");
    let experiment_label = experiments_form.elements.experiment;
    let experiment_id = experiment_label.experiment_id;

    let endpoint = getMongoURLfromUI();
    let headers = [{"header": "Accept", "value": "application/json"}];
    let mongo_REST_endpoint = endpoint + "/experiments/" + experiment_id;
    sendCORSrequest("GET", mongo_REST_endpoint, headers, 200, function (response) {
        propagateExperimentTimes(response)
    }, "Error getting experiment times");
}


export function deleteExperiment(experiment, check_confirm) {
    "use strict";
    if (check_confirm) {
        let r = confirm("Are you sure do you want to delete the experiment?");
        if (r === false) {
            return
        }
    }

    let experiments_form;
    let experiment_label;
    let experiment_id;
    let experiment_etag;

    if (experiment) {
        experiment_id = experiment.experiment_id;
        experiment_etag = experiment.etag;
    } else {
        experiments_form = document.getElementById("experiment_picker");
        experiment_label = experiments_form.elements.experiment;
        experiment_id = experiment_label.experiment_id;
        experiment_etag = experiment_label.etag;
    }

    let endpoint = getMongoURLfromUI();
    let headers = [{"header": "Accept", "value": "application/json"}, {"header": "If-Match", "value": experiment_etag}];
    let mongo_REST_endpoint = endpoint + "/experiments/" + experiment_id;

    let success_function = function (response) {
        deleted_experiments.push(experiment_id)
    };

    sendCORSrequest("DELETE", mongo_REST_endpoint,
        headers, 204, success_function,
        "Error deleting experiment information");
}

function propagateExperimentTimes(experiment) {
    "use strict";
    let times = document.getElementById("times_form");
    times.elements.start_time.value = timeConverter(experiment.start_time);
    times.elements.end_time.value = timeConverter(experiment.end_time);

}

function experiment_label_on_click() {
    "use strict";
    let experiments_form = document.getElementById("experiment_picker");
    let experiment_label = experiments_form.elements.experiment;
    experiment_label.value = this.label_value;
    experiment_label.experiment_id = this.experiment_id;
    experiment_label.etag = this.etag;
}

function experiment_delete_on_click() {
    "use strict";
    var experiment = {};
    experiment.experiment_id = this.experiment_id;
    experiment.etag = this.etag;
    deleteExperiment(experiment, false);
}

function populateExperimentsDropdown(experiments, remove_previous) {
    "use strict";
    let list = document.getElementById("exps_timepicker_list");

    if (remove_previous) {
        while (list.firstChild) {
            list.removeChild(list.firstChild);
        }
    }

    experiments._items.sort(function (a, b) {
        if (a.start_time < b.start_time) return -1;
        if (a.start_time > b.start_time) return 1;
        return 0;
    });


    for (let experiment of experiments._items) {
        if (deleted_experiments.includes(experiment._id)) {
            continue
        }

        let child = document.createElement("li");

        let button1 = document.createElement("div");
        button1.innerHTML = "Set: " + experiment.experiment_id.bold();
        button1.classList = "btn btn-default ";
        button1.label_value = experiment.experiment_id;
        button1.experiment_id = experiment._id;
        button1.etag = experiment._etag;
        button1.onclick = experiment_label_on_click;
        child.appendChild(button1);

        let button2 = document.createElement("div");
        button2.innerHTML = "Delete";
        button2.classList = "btn btn-default ";
        button2.experiment_id = experiment._id;
        button2.etag = experiment._etag;
        button2.onclick = experiment_delete_on_click;
        child.appendChild(button2);

        list.append(child);
    }
}

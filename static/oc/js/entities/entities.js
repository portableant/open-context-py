/*
 * ------------------------------------------------------------------
	AJAX for entity searches
 * ------------------------------------------------------------------
*/

/* DOM id for input element with search string */
var search_text_domID = "entity-string"; 
/* DOM id for <ul> element where entity search results go */
var searchEntityListDomID = "search-entity-list";
var selectFoundEntityFunction = "selectEntity";
var entities_panel_title = "Entity Lookup";
var limit_item_type = false;
var limit_class_uri = false;
var limit_project_uuid = false;
var limit_vocab_uri = false;

function generateEntitiesInterface(selectReadOnly, additionalButton){
	/* returns a HTML string to generate an entities search interface */
	if (selectReadOnly) {
		selectReadOnly = "readonly";
	}
	else{
		selectReadOnly = "";
	}
	selectReadOnly = selectReadOnly || "readonly";
	if (additionalButton != false) {
		//request to add an additional button to add more functionality
		var disabled = "";
		if (additionalButton.buttonDisabled) {
			disabled = "disabled=\"disabled\"";
		}
		var buttonGroupHTML = [
			"<div class=\"form-group form-group-sm\">",
				"<label for=\"sel-added-control\" class=\"col-xs-2 control-label\">" + additionalButton.label + "</label>",
					"<div class=\"col-xs-10\">",
						"<button id=\"" + additionalButton.buttonID + "\" style=\"margin-bottom:1%;\" type=\"button\" ",
						"class=\"" + additionalButton.buttonClass + "\" onclick=\"javascript:" + additionalButton.funct + ";\"",
						disabled + ">",
						"<span class=\"" + additionalButton.icon + "\"></span>",
						" " + additionalButton.buttonText + "</button>",
					"</div>",
				"</div>"
		].join("\n");
	}
	else{
		var buttonGroupHTML = "";
	}
	
	var interfaceString = [	
		"<div class=\"panel panel-default\">",
			"<div class=\"panel-heading\">",
				"<h4 class=\"panel-title\">" + entities_panel_title + "</h4>",
			"</div>",
			"<div class=\"panel-body\">",
				"<form class=\"form-horizontal\" role=\"form\">",
					"<div class=\"form-group form-group-sm\">",
						"<label for=\"sel-entity-label\" class=\"col-xs-2 control-label\">Label</label>",
						"<div class=\"col-xs-10\">",
							"<input id=\"sel-entity-label\" type=\"text\"  value=\"\" placeholder=\"Select an entity\" class=\"form-control input-sm\" " + selectReadOnly + "/>",
						"</div>",
					"</div>",
					"<div class=\"form-group form-group-sm\">",
						"<label for=\"sel-entity-id\" class=\"col-xs-2 control-label\">ID</label>",
						"<div class=\"col-xs-10\">",
							"<input id=\"sel-entity-id\" type=\"text\"  value=\"\" placeholder=\"Select an entity\" class=\"form-control input-sm\" " + selectReadOnly + "/>",
						"</div>",
					"</div>",
					buttonGroupHTML,
					"<div class=\"form-group form-group-sm\">",
						"<label for=\"entity-string\" class=\"col-xs-2 control-label\">Search</label>",
						"<div class=\"col-xs-10\">",
							"<input id=\"" + search_text_domID + "\" type=\"text\"  value=\"\" onkeydown=\"javascript:searchEntities();\" class=\"form-control input-sm\" />",
						"</div>",
					"</div>",
				"</form>",
				"<ul id=\"" + searchEntityListDomID + "\">",
				"</ul>",
			"</div>",
		"</div>"].join("\n");
	return interfaceString;
}

function searchEntities(){
	/* AJAX call to search entities filtered by a search-string */
	var qstring = document.getElementById(search_text_domID).value;
	var searchEntityListDom = document.getElementById(searchEntityListDomID);
	searchEntityListDom.innerHTML = "<li>Searching for '" + qstring + "'...</li>";
	var url = "../../entities/look-up/";
	var data = { q:qstring };
	if (limit_class_uri != false) {
		data['class_uri'] = limit_class_uri;
	}
	if (limit_project_uuid != false) {
		data['project_uuid'] = limit_project_uuid;
	}
	if (limit_vocab_uri != false) {
		data['vocab_uri'] = limit_vocab_uri;
	}
	if (limit_item_type != false) {
		url += limit_item_type;
	}
	else{
		url += "0";
	}
	var req = $.ajax({
		type: "GET",
		url: url,
		dataType: "json",
		data: data,
		success: searchEntitiesDone
	});
}

function searchEntitiesDone(data){
	/* Displays list of entities that meet search criteria */
	var searchEntityListDom = document.getElementById(searchEntityListDomID);
	searchEntityListDom.innerHTML = "";
	for (var i = 0, length = data.length; i < length; i++) {
		var newListItem = document.createElement("li");
		newListItem.id = "search-entity-item-" + i;
		var entityIDdomID = "search-entity-id-" + i;
		var linkHTML = generateEntityLink(entityIDdomID, data[i].type, data[i].id, data[i].id);
		var entityString = "<a href=\"javascript:" + selectFoundEntityFunction + "(" + i + ")\" id=\"search-entity-label-" + i + "\" >" + data[i].label + "</a>";
		// entityString += "<br/><small id=\"search-entity-id-" + i + "\">" + data[i].id + "</small>";
		entityString += "<br/><small>" + linkHTML + "</small>";
		newListItem.innerHTML = entityString;
		searchEntityListDom.appendChild(newListItem);
	}
}

function selectEntity(item_num) {
	/* Adds selected entity label and ID to the right dom element */
	var act_domID = "search-entity-id-" + item_num;
	var item_id = document.getElementById(act_domID).innerHTML;
	var sel_id_dom = document.getElementById("sel-entity-id");
	sel_id_dom.value = item_id;
	act_domID =  "search-entity-label-" + item_num;
	var item_label = document.getElementById(act_domID).innerHTML;
	var sel_label_dom = document.getElementById("sel-entity-label");
	sel_label_dom.value = item_label;
}

function generateEntityLink(nodeID, entity_type, entity_id, entity_label){
	var linkHTML = "";
	var labelSpan = "<span id=\"" + nodeID + "\">" + entity_label + "</span>";
	if (entity_type != "uri" && entity_type != "import-field" && entity_type != "user-typed-link") {
		var icon = "<span class=\"glyphicon glyphicon-new-window\"></span> ";
		linkHTML = "<a title=\"View in new tab\" href=\"../../" + entity_type + "/" + entity_id + "\" target=\"_blank\">" + icon + labelSpan + "</a>";
	}
	else if (entity_type == "uri") {
		var icon = "<span class=\"glyphicon glyphicon-new-window\"></span> ";
		linkHTML = "<a title=\"View in new tab\" href=\"" + entity_id + "\" target=\"_blank\">" + icon + labelSpan + "</a>";
	}
	else{
		if (entity_type == "user-typed-link") {
			var icon = "<span class=\"glyphicon glyphicon-new-window\"></span> ";
		}
		linkHTML = labelSpan;
	}
	return linkHTML;
}


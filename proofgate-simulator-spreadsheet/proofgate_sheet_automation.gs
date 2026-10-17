// Google Apps Script: proofgate_sheet_automation.gs
// Este script adiciona funções utilitárias em uma cópia do Google Sheet gerado a partir do Excel.
// - cria menus para "Inject Scenario" e "Run Selected Run"
// - função exemplo para injetar cenários copiando valores das abas Scenarios para Market_Evidence / Agent_Intent / Runs

function onOpen() {
  SpreadsheetApp.getUi().createMenu('ProofGate')
    .addItem('Inject Scenario...', 'showScenarioDialog')
    .addItem('Run Selected Run', 'runSelectedRun')
    .addToUi();
}

function showScenarioDialog() {
  var html = HtmlService.createHtmlOutput('<p>Select scenario by ID and click Inject (this needs implementation)</p>');
  SpreadsheetApp.getUi().showModalDialog(html, 'Inject Scenario');
}

function injectScenarioById(scenarioId) {
  var ss = SpreadsheetApp.getActive();
  var scenarios = ss.getSheetByName('05_Scenarios');
  var runs = ss.getSheetByName('06_Runs');
  var data = scenarios.getDataRange().getValues();
  for (var i = 1; i < data.length; i++) {
    if (data[i][0] == scenarioId) {
      var mandateOverrides = data[i][3];
      var evidenceOverrides = data[i][4];
      var intentOverrides = data[i][5];
      // Parse JSON strings if necessary and apply to a new run row (simplified example)
      var newRow = runs.getLastRow() + 1;
      runs.getRange(newRow, 1).setValue('RUN_' + Utilities.getUuid());
      runs.getRange(newRow, 2).setValue(new Date());
      runs.getRange(newRow, 5).setValue('M_DEFAULT');
      // For evidence selection, you may create a new evidence row in 03_Market_Evidence and reference it
      return true;
    }
  }
  return false;
}

const SPREADSHEET_ID = "REPLACE_WITH_SPREADSHEET_ID";
const SHEET_NAME = "Engineer Responses";

function doGet() {
  return HtmlService.createHtmlOutputFromFile("Index")
    .setTitle("MAI Mobile Engineer Insight Form")
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

function submitResponse(formData) {
  validateConfig_();

  const sheet = getOrCreateSheet_();
  const row = [
    new Date(),
    sanitize_(formData.engineerName),
    sanitize_(formData.teamRole),
    sanitize_(formData.patternRepeat),
    sanitize_(formData.falseConsistency),
    sanitize_(formData.hardcodedSharedCandidate),
    sanitize_(formData.largeSpecificImpact),
    sanitize_(formData.reusablePreference),
    sanitize_(formData.slotFeasibility),
    sanitize_(formData.topStandardizationAreas),
    sanitize_(formData.extraNotes)
  ];

  sheet.appendRow(row);

  return {
    ok: true,
    message: "Jawaban berhasil disimpan. Terima kasih."
  };
}

function validateConfig_() {
  if (!SPREADSHEET_ID || SPREADSHEET_ID === "REPLACE_WITH_SPREADSHEET_ID") {
    throw new Error("SPREADSHEET_ID belum diisi di Code.gs.");
  }
}

function getOrCreateSheet_() {
  const spreadsheet = SpreadsheetApp.openById(SPREADSHEET_ID);
  let sheet = spreadsheet.getSheetByName(SHEET_NAME);

  if (!sheet) {
    sheet = spreadsheet.insertSheet(SHEET_NAME);
    sheet.appendRow([
      "Timestamp",
      "Engineer Name",
      "Team / Role",
      "Pattern Repeat",
      "False Consistency",
      "Hardcoded Shared Candidate",
      "Large Specific Component Impact",
      "Preferred Reusable Shape",
      "Slot Scaffold Feasibility",
      "Top 3 Standardization Areas",
      "Extra Notes"
    ]);
    sheet.setFrozenRows(1);
  }

  return sheet;
}

function sanitize_(value) {
  return value == null ? "" : String(value).trim();
}

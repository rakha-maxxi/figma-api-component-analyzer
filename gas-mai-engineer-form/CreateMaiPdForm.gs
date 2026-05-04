/**
 * MAI Product Designer Insight Form
 *
 * This script creates a native Google Form for collecting
 * Product Designer input related to Design Ops, UI kit usage,
 * local component behavior, and promotion opportunities in MAI.
 *
 * How to use:
 * 1. Open a new Google Apps Script project.
 * 2. Paste this whole file into the script editor.
 * 3. Replace SPREADSHEET_ID if you want responses in a specific sheet.
 * 4. Run createMaiPdForm().
 * 5. Open the logged URLs from Apps Script execution log.
 */

const PD_SPREADSHEET_ID = "REPLACE_WITH_SPREADSHEET_ID";
const PD_FORM_TITLE = "MAI Product Designer Insight";
const PD_SHEET_NAME = "PD Responses";

function createMaiPdForm() {
  const form = FormApp.create(PD_FORM_TITLE)
    .setDescription(
      [
        "Form ini dipakai untuk bantu Design Ops memahami cara kerja Product Designer di MAI,",
        "kapan existing component membantu, kapan designer membuat local component,",
        "dan reusable structure apa yang paling worth untuk dibantu lebih dulu."
      ].join(" ")
    )
    .setConfirmationMessage(
      "Terima kasih. Jawabanmu akan dipakai untuk membantu arah UI kit dan workflow Design Ops di MAI."
    )
    .setProgressBar(true)
    .setShuffleQuestions(false)
    .setAllowResponseEdits(false)
    .setLimitOneResponsePerUser(false);

  addPdIntroSection_(form);
  addPdIdentity_(form);
  addPdWorkflowQuestions_(form);
  addPdComponentQuestions_(form);
  addPdClosingSection_(form);

  if (PD_SPREADSHEET_ID && PD_SPREADSHEET_ID !== "REPLACE_WITH_SPREADSHEET_ID") {
    form.setDestination(FormApp.DestinationType.SPREADSHEET, PD_SPREADSHEET_ID);
    renamePdResponseSheet_(PD_SPREADSHEET_ID, PD_SHEET_NAME);
  }

  Logger.log("PD Form edit URL: %s", form.getEditUrl());
  Logger.log("PD Form live URL: %s", form.getPublishedUrl());
  Logger.log("PD Form ID: %s", form.getId());
}

function addPdIntroSection_(form) {
  form.addSectionHeaderItem()
    .setTitle("Konteks")
    .setHelpText(
      "Jawaban boleh singkat dan praktis. Fokusnya bukan jawaban formal, tapi insight yang benar-benar kepakai untuk membantu arah UI kit dan support Design Ops di MAI."
    );
}

function addPdIdentity_(form) {
  form.addTextItem()
    .setTitle("Nama Product Designer")
    .setRequired(true);

  form.addTextItem()
    .setTitle("Project / platform yang paling sering dikerjakan")
    .setHelpText("Contoh: MM+ tablet, FS+ mobile, Backoffice web")
    .setRequired(true);
}

function addPdWorkflowQuestions_(form) {
  form.addParagraphTextItem()
    .setTitle("1. Saat mulai desain feature baru, biasanya kamu mulai dari existing component atau bikin layout dulu?")
    .setHelpText("Ceritakan cara kerja yang paling sering kamu lakukan saat ini.")
    .setRequired(true);

  form.addParagraphTextItem()
    .setTitle("2. Dalam workflow sekarang, kapan existing UI kit atau master component terasa paling membantu?")
    .setRequired(true);

  form.addParagraphTextItem()
    .setTitle("3. Dalam kondisi kerja sekarang, kapan kamu biasanya memutuskan bikin local component atau side component sendiri?")
    .setHelpText("Contoh: saat kejar MVP, saat komponen belum ada, saat existing component terlalu rigid, dan lainnya.")
    .setRequired(true);
}

function addPdComponentQuestions_(form) {
  form.addParagraphTextItem()
    .setTitle("4. Apa yang paling bikin existing component susah dipakai atau akhirnya tidak kamu pakai?")
    .setHelpText("Contoh: susah dicari, terlalu besar, terlalu spesifik, kurang fleksibel, atau layer-nya ribet.")
    .setRequired(true);

  form.addParagraphTextItem()
    .setTitle("5. Pola UI atau section apa yang paling sering kamu ulang manual di banyak file atau feature?")
    .setHelpText("Contoh: section header, card summary, dialog, text pairing, filter bar, bottom action, dan lainnya.")
    .setRequired(true);

  form.addParagraphTextItem()
    .setTitle("6. Kalau ada scaffold atau slot-based component, misalnya section shell, card shell, header shell, apakah itu terasa membantu workflow kamu?")
    .setHelpText("Boleh jelaskan bagian mana yang terasa membantu atau justru berpotensi bikin ribet.")
    .setRequired(true);

  form.addCheckboxItem()
    .setTitle("7. Bentuk support UI kit seperti apa yang menurutmu paling membantu kerja cepat tapi tetap konsisten?")
    .setChoiceValues([
      "Token yang lebih konsisten dan jelas",
      "Atomic component seperti button, input, chip, badge",
      "Compound component seperti text pairing, stat pair, section header",
      "Scaffold seperti section shell, card shell, dialog shell",
      "Pattern/reference yang sudah agak jadi",
      "Dokumentasi penggunaan dan do/don't",
      "Naming dan struktur file yang lebih rapi"
    ])
    .showOtherOption(true)
    .setRequired(true);

  form.addParagraphTextItem()
    .setTitle("8. Kalau kamu bisa minta 3 reusable component atau scaffold dibantu dulu oleh Design Ops, kamu akan pilih apa?")
    .setHelpText("Tulis 3 prioritas yang paling terasa impact-nya buat kerja kamu.")
    .setRequired(true);

  form.addParagraphTextItem()
    .setTitle("9. Ada local component atau pattern yang menurutmu sudah cukup matang dan layak dipromosikan ke project UI kit?")
    .setHelpText("Kalau ada, boleh kasih contoh dan alasannya.")
    .setRequired(true);
}

function addPdClosingSection_(form) {
  form.addParagraphTextItem()
    .setTitle("Catatan tambahan")
    .setHelpText("Tambahan insight, contoh kasus, atau concern lain terkait UI kit, local component, dan workflow desain.")
    .setRequired(false);
}

function renamePdResponseSheet_(spreadsheetId, expectedSheetName) {
  const spreadsheet = SpreadsheetApp.openById(spreadsheetId);
  const sheets = spreadsheet.getSheets();
  const responseSheet = sheets[sheets.length - 1];

  if (responseSheet.getName() !== expectedSheetName) {
    responseSheet.setName(expectedSheetName);
  }
}

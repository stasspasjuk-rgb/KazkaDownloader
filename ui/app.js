// KazkaDownloader Frontend Controller

const I18N = {
  ru: {
    lang_code: "RU",
    history_nav: "История",
    label_url: "Ссылка на видео",
    placeholder_url: "https://www.youtube.com/watch?v=...",
    btn_paste: "Вставить",
    label_folder: "Папка сохранения",
    btn_browse: "Обзор",
    label_quality: "Качество",
    opt_max: "Максимальное",
    opt_audio: "Только аудио (MP3)",
    btn_download: "СКАЧАТЬ",
    btn_downloading: "СКАЧИВАНИЕ...",
    label_log: "Лог",
    history_title: "История скачек",
    btn_back: "← Назад к скачиванию",
    btn_open: "Открыть",
    btn_folder: "Папка",
    select_lang_title: "Выбери язык",
    promo_title: "Знал ли ты?",
    promo_text_1: "Что kazkavpn один из лучший дешевых ВПН с обходом блокировок, а так-же бесплатный пробный период",
    promo_text_2: "Снизу ты видишь промокод который дает тебе скиду 10% на покупку впн!",
    btn_continue: "ПРОДОЛЖИТЬ",
    copied_toast: "Промокод скопирован в буфер обмена!",
    copied_short: "Скопировано!",
    empty_history: "История скачек пуста. Скачайте первое видео!",
    err_no_url: "Пожалуйста, укажите ссылку на видео!",
    download_success: "Видео успешно скачано!"
  },
  en: {
    lang_code: "EN",
    history_nav: "History",
    label_url: "Video link",
    placeholder_url: "https://www.youtube.com/watch?v=...",
    btn_paste: "Paste",
    label_folder: "Save folder",
    btn_browse: "Browse",
    label_quality: "Quality",
    opt_max: "Best quality",
    opt_audio: "Audio only (MP3)",
    btn_download: "DOWNLOAD",
    btn_downloading: "DOWNLOADING...",
    label_log: "Log",
    history_title: "Download history",
    btn_back: "← Back to downloader",
    btn_open: "Open",
    btn_folder: "Folder",
    select_lang_title: "Select language",
    promo_title: "Did you know?",
    promo_text_1: "Kazkavpn is one of the best low-cost VPNs for bypassing blocks, and it also offers a free trial period.",
    promo_text_2: "Below, you'll find a promo code that gives you a 10% discount on your VPN purchase!",
    btn_continue: "CONTINUE",
    copied_toast: "Promo code copied to clipboard!",
    copied_short: "Copied!",
    empty_history: "Download history is empty. Download your first video!",
    err_no_url: "Please enter a video URL!",
    download_success: "Video successfully downloaded!"
  }
};

let currentLang = "ru";
let appConfig = {};
let appHistory = [];
let isDownloading = false;
let isOnboardingFlow = false;

// DOM Elements
const elLangCode = document.getElementById("current-lang-code");
const elBtnLangToggle = document.getElementById("btn-lang-toggle");
const elBtnHistoryToggle = document.getElementById("btn-history-toggle");
const elBtnTelegram = document.getElementById("btn-telegram");
const elBtnBrand = document.getElementById("btn-brand");

const elViewDownloader = document.getElementById("view-downloader");
const elViewHistory = document.getElementById("view-history");
const elBtnBackToDownload = document.getElementById("btn-back-to-download");

const elInputUrl = document.getElementById("input-url");
const elBtnPaste = document.getElementById("btn-paste");
const elInputFolder = document.getElementById("input-folder");
const elBtnBrowse = document.getElementById("btn-browse");
const elSelectQuality = document.getElementById("select-quality");
const elBtnDownload = document.getElementById("btn-download");
const elBtnDownloadText = document.getElementById("btn-download-text");

const elProgressContainer = document.getElementById("progress-container");
const elProgressBarFill = document.getElementById("progress-bar-fill");
const elProgressPercent = document.getElementById("progress-percent");
const elProgressSpeed = document.getElementById("progress-speed");
const elProgressEta = document.getElementById("progress-eta");

const elLogBox = document.getElementById("log-box");
const elHistoryItemsContainer = document.getElementById("history-items-container");

const elModalLanguage = document.getElementById("modal-language");
const elBtnSelectRu = document.getElementById("btn-select-ru");
const elBtnSelectEn = document.getElementById("btn-select-en");
const elOptLangRu = document.getElementById("opt-lang-ru");
const elOptLangEn = document.getElementById("opt-lang-en");
const elModalLangTg = document.getElementById("modal-lang-tg");

const elModalPromo = document.getElementById("modal-promo");
const elModalPromoTg = document.getElementById("modal-promo-tg");
const elPromocodeValue = document.getElementById("promocode-value");
const elBtnCopyCode = document.getElementById("btn-copy-code");
const elBtnClosePromo = document.getElementById("btn-close-promo");

const elToast = document.getElementById("toast");

// Toast helper
function showToast(message) {
  elToast.textContent = message;
  elToast.classList.add("show");
  clearTimeout(elToast._timer);
  elToast._timer = setTimeout(() => {
    elToast.classList.remove("show");
  }, 3000);
}

// Log message helper
function appendLog(text, type = "normal") {
  const line = document.createElement("div");
  line.className = "log-line";
  if (type === "success") line.classList.add("log-success");
  if (type === "error") line.classList.add("log-error");
  if (type === "warning") line.classList.add("log-warning");
  line.textContent = text;
  elLogBox.appendChild(line);
  elLogBox.scrollTop = elLogBox.scrollHeight;
}

// Language / Translation handler
function applyTranslations(lang) {
  currentLang = lang;
  const t = I18N[lang] || I18N.ru;
  
  elLangCode.textContent = t.lang_code;

  document.querySelectorAll("[data-i18n]").forEach(el => {
    const key = el.getAttribute("data-i18n");
    if (t[key]) {
      el.textContent = t[key];
    }
  });

  elInputUrl.placeholder = t.placeholder_url;
  
  if (isDownloading) {
    elBtnDownloadText.textContent = t.btn_downloading;
  } else {
    elBtnDownloadText.textContent = t.btn_download;
  }
}

// Switch Views
function showView(viewName) {
  if (viewName === "history") {
    elViewDownloader.style.display = "none";
    elViewHistory.style.display = "block";
    renderHistory(appHistory);
  } else {
    elViewHistory.style.display = "none";
    elViewDownloader.style.display = "block";
  }
}

// Render History
function renderHistory(items) {
  elHistoryItemsContainer.innerHTML = "";
  const t = I18N[currentLang] || I18N.ru;

  if (!items || items.length === 0) {
    const empty = document.createElement("div");
    empty.className = "history-empty";
    empty.textContent = t.empty_history;
    elHistoryItemsContainer.appendChild(empty);
    return;
  }

  items.forEach(item => {
    const row = document.createElement("div");
    row.className = "history-item";

    const info = document.createElement("div");
    info.className = "item-info";

    const title = document.createElement("div");
    title.className = "item-title";
    title.textContent = item.title || "Video";
    title.title = item.title || "";

    const meta = document.createElement("div");
    meta.className = "item-meta";
    meta.textContent = `${item.timestamp || ""} • ${item.size || ""}`;

    info.appendChild(title);
    info.appendChild(meta);

    const actions = document.createElement("div");
    actions.className = "item-actions";

    // Open file button
    const btnOpen = document.createElement("button");
    btnOpen.className = "history-btn";
    btnOpen.innerHTML = `<img src="assets/play.svg" alt=""> <span>${t.btn_open}</span>`;
    btnOpen.onclick = () => {
      if (window.pywebview && window.pywebview.api) {
        window.pywebview.api.open_file(item.filepath);
      }
    };

    // Open folder button
    const btnFolder = document.createElement("button");
    btnFolder.className = "history-btn";
    btnFolder.innerHTML = `<img src="assets/folder.svg" alt=""> <span>${t.btn_folder}</span>`;
    btnFolder.onclick = () => {
      if (window.pywebview && window.pywebview.api) {
        window.pywebview.api.open_folder(item.filepath);
      }
    };

    // Delete item button
    const btnDel = document.createElement("button");
    btnDel.className = "history-btn history-btn-del";
    btnDel.innerHTML = `<img src="assets/close.svg" alt="✖">`;
    btnDel.title = "Удалить из истории";
    btnDel.onclick = () => {
      if (window.pywebview && window.pywebview.api) {
        window.pywebview.api.delete_history_item(item.id).then(res => {
          if (res && res.history) {
            appHistory = res.history;
            renderHistory(appHistory);
          }
        });
      }
    };

    actions.appendChild(btnOpen);
    actions.appendChild(btnFolder);
    actions.appendChild(btnDel);

    row.appendChild(info);
    row.appendChild(actions);

    elHistoryItemsContainer.appendChild(row);
  });
}

// Copy Promocode
function copyPromo() {
  const code = elPromocodeValue.textContent.trim();
  const t = I18N[currentLang] || I18N.ru;

  if (window.pywebview && window.pywebview.api) {
    window.pywebview.api.copy_text(code);
  } else if (navigator.clipboard) {
    navigator.clipboard.writeText(code);
  }

  showToast(t.copied_toast);
  
  elBtnCopyCode.style.transform = "scale(1.2)";
  setTimeout(() => {
    elBtnCopyCode.style.transform = "scale(1)";
  }, 200);
}

// Initialize Application state from Python
function initApp() {
  if (!window.pywebview || !window.pywebview.api) {
    console.warn("pywebview API not yet available, waiting...");
    return;
  }

  window.pywebview.api.get_state().then(state => {
    if (!state) return;
    appConfig = state.config || {};
    appHistory = state.history || [];

    // Set save dir
    if (appConfig.save_dir) {
      elInputFolder.value = appConfig.save_dir;
    }

    // Set quality
    if (appConfig.quality) {
      elSelectQuality.value = appConfig.quality;
    }

    // Set language
    const lang = appConfig.language || "ru";
    applyTranslations(lang);

    // Onboarding flow: if first time, show Language Modal first
    if (!appConfig.onboarding_completed) {
      isOnboardingFlow = true;
      elModalLanguage.style.display = "flex";
    }

    // Notify backend that client is ready to receive logs and verify components
    window.pywebview.api.client_ready();
  });
}

// Event Listeners
document.addEventListener("DOMContentLoaded", () => {

  // Brand logo click -> go to main downloader
  elBtnBrand.addEventListener("click", () => {
    showView("downloader");
  });

  // Language toggle -> opens language modal
  elBtnLangToggle.addEventListener("click", () => {
    isOnboardingFlow = false;
    elModalLanguage.style.display = "flex";
  });

  // History button -> toggle view
  elBtnHistoryToggle.addEventListener("click", () => {
    if (elViewHistory.style.display === "none") {
      showView("history");
    } else {
      showView("downloader");
    }
  });

  elBtnBackToDownload.addEventListener("click", () => {
    showView("downloader");
  });

  // Telegram buttons
  const openTelegram = () => {
    if (window.pywebview && window.pywebview.api) {
      window.pywebview.api.open_telegram();
    } else {
      window.open("https://t.me/kazkavpn", "_blank");
    }
  };

  elBtnTelegram.addEventListener("click", openTelegram);
  elModalLangTg.addEventListener("click", openTelegram);
  elModalPromoTg.addEventListener("click", openTelegram);

  // Paste URL button
  elBtnPaste.addEventListener("click", () => {
    if (window.pywebview && window.pywebview.api) {
      window.pywebview.api.get_clipboard().then(res => {
        if (res && res.text) {
          elInputUrl.value = res.text.trim();
        } else if (navigator.clipboard) {
          navigator.clipboard.readText().then(text => {
            elInputUrl.value = text.trim();
          }).catch(() => {});
        }
      });
    } else if (navigator.clipboard) {
      navigator.clipboard.readText().then(text => {
        elInputUrl.value = text.trim();
      }).catch(() => {});
    }
  });

  // Browse folder button
  elBtnBrowse.addEventListener("click", () => {
    if (window.pywebview && window.pywebview.api) {
      window.pywebview.api.select_folder().then(res => {
        if (res && res.folder) {
          elInputFolder.value = res.folder;
        }
      });
    }
  });

  // Download button
  elBtnDownload.addEventListener("click", () => {
    const t = I18N[currentLang] || I18N.ru;
    const url = elInputUrl.value.trim();

    if (!url) {
      showToast(t.err_no_url);
      elInputUrl.focus();
      return;
    }

    if (isDownloading) {
      return;
    }

    isDownloading = true;
    elBtnDownload.classList.add("downloading");
    elBtnDownloadText.textContent = t.btn_downloading;
    elProgressContainer.style.display = "block";
    elProgressBarFill.style.width = "0%";
    elProgressPercent.textContent = "0%";
    elProgressSpeed.textContent = "--";
    elProgressEta.textContent = "--";

    const folder = elInputFolder.value.trim();
    const quality = elSelectQuality.value;

    appendLog(`Запуск скачивания: ${url}`);

    if (window.pywebview && window.pywebview.api) {
      window.pywebview.api.start_download(url, folder, quality);
    }
  });

  // Language Selection inside Modal
  const selectLanguage = (lang) => {
    applyTranslations(lang);
    if (window.pywebview && window.pywebview.api) {
      window.pywebview.api.set_language(lang);
    }
    elModalLanguage.style.display = "none";

    // If in onboarding flow, next show Promo modal (Surface Book 2 / 4)
    if (isOnboardingFlow) {
      elModalPromo.style.display = "flex";
    }
  };

  elOptLangRu.addEventListener("click", () => selectLanguage("ru"));
  elBtnSelectRu.addEventListener("click", (e) => {
    e.stopPropagation();
    selectLanguage("ru");
  });

  elOptLangEn.addEventListener("click", () => selectLanguage("en"));
  elBtnSelectEn.addEventListener("click", (e) => {
    e.stopPropagation();
    selectLanguage("en");
  });

  // Promocode actions
  elPromocodeValue.addEventListener("click", copyPromo);
  elBtnCopyCode.addEventListener("click", copyPromo);

  elBtnClosePromo.addEventListener("click", () => {
    elModalPromo.style.display = "none";
    if (isOnboardingFlow) {
      isOnboardingFlow = false;
      if (window.pywebview && window.pywebview.api) {
        window.pywebview.api.complete_onboarding();
      }
    }
  });

});

// Global callbacks invoked from Python
window.onLog = function(data) {
  if (data && data.message) {
    appendLog(data.message);
  }
};

window.onProgress = function(data) {
  if (!data) return;
  if (data.percent !== undefined) {
    elProgressBarFill.style.width = `${data.percent}%`;
    elProgressPercent.textContent = `${data.percent}%`;
  }
  if (data.speed) {
    elProgressSpeed.textContent = data.speed;
  }
  if (data.eta) {
    elProgressEta.textContent = `ETA: ${data.eta}`;
  }
};

window.onDownloadFinished = function(data) {
  isDownloading = false;
  elBtnDownload.classList.remove("downloading");
  const t = I18N[currentLang] || I18N.ru;
  elBtnDownloadText.textContent = t.btn_download;
  
  if (data && data.success) {
    elProgressBarFill.style.width = "100%";
    elProgressPercent.textContent = "100%";
    showToast(t.download_success);
    if (data.history) {
      appHistory = data.history;
      renderHistory(appHistory);
    }
  } else {
    appendLog("Скачивание остановлено с ошибкой.", "error");
  }

  setTimeout(() => {
    if (!isDownloading) {
      elProgressContainer.style.display = "none";
    }
  }, 4000);
};

// pywebviewready listener
window.addEventListener("pywebviewready", () => {
  initApp();
});

// Fallback init in case pywebview is already attached
if (window.pywebview && window.pywebview.api) {
  initApp();
}

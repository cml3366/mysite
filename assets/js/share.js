// 分享：按当前页面地址填好各平台链接；微信与页眉分享按钮打开二维码弹窗；复制链接与知乎写入剪贴板
(function () {
  var script = document.currentScript;
  var qrApi = script ? script.getAttribute("data-qr-api") : "";
  var url = location.href.split("#")[0];
  var title = document.title;
  var u = encodeURIComponent(url);
  var t = encodeURIComponent(title);

  var links = {
    weibo: "https://service.weibo.com/share/share.php?url=" + u + "&title=" + t,
    qzone: "https://sns.qzone.qq.com/cgi-bin/qzshare/cgi_qzshare_onekey?url=" + u + "&title=" + t,
    x: "https://twitter.com/intent/tweet?url=" + u + "&text=" + t,
    facebook: "https://www.facebook.com/sharer/sharer.php?u=" + u,
    telegram: "https://t.me/share/url?url=" + u + "&text=" + t,
  };

  var modal = document.getElementById("sk-share-modal");
  var mask = document.getElementById("sk-share-mask");

  function openModal() {
    if (!modal) return;
    var img = document.getElementById("sk-share-qr");
    if (img && !img.src) img.src = qrApi.replace("{url}", u);
    document.getElementById("sk-share-url").textContent = url;
    modal.hidden = false;
    mask.hidden = false;
    document.getElementById("sk-share-close").focus();
  }

  function closeModal() {
    if (!modal) return;
    modal.hidden = true;
    mask.hidden = true;
  }

  function copy(btn) {
    var label = btn.querySelector(".sk-share-label");
    var old = label.textContent;
    var done = function (text) {
      label.textContent = text;
      btn.classList.add("is-done");
      setTimeout(function () {
        label.textContent = old;
        btn.classList.remove("is-done");
      }, 1500);
    };
    var ok = function () {
      done(btn.dataset.share === "zhihu" ? "已复制，去知乎粘贴" : "已复制");
    };
    // 旧浏览器或剪贴板权限被拒时，退回 execCommand
    var fallback = function () {
      var ta = document.createElement("textarea");
      ta.value = url;
      ta.setAttribute("readonly", "");
      ta.style.position = "fixed";
      ta.style.opacity = "0";
      document.body.appendChild(ta);
      ta.select();
      var copied = false;
      try {
        copied = document.execCommand("copy");
      } catch (e) {}
      document.body.removeChild(ta);
      copied ? ok() : done("复制失败");
    };
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(url).then(ok, fallback);
    } else {
      fallback();
    }
  }

  document.querySelectorAll("[data-share]").forEach(function (btn) {
    var key = btn.dataset.share;
    if (links[key]) {
      btn.href = links[key];
      btn.target = "_blank";
    } else if (key === "wechat") {
      btn.addEventListener("click", function (e) {
        e.preventDefault();
        openModal();
      });
    } else if (key === "copy" || key === "zhihu") {
      btn.addEventListener("click", function (e) {
        e.preventDefault();
        copy(btn);
      });
    }
  });

  document.querySelectorAll(".sk-share-open").forEach(function (btn) {
    btn.addEventListener("click", openModal);
  });
  if (mask) mask.addEventListener("click", closeModal);
  var closeBtn = document.getElementById("sk-share-close");
  if (closeBtn) closeBtn.addEventListener("click", closeModal);
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closeModal();
  });
})();

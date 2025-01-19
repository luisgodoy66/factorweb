! function (e, t) {
    "object" == typeof exports && "undefined" != typeof module ? module.exports = t() : "function" == typeof define && define.amd ? define(t) : (e = e || self).Sweetalert2 = t()
}(this, function () {
    "use strict";
    const u = Object.freeze({
            cancel: "cancel",
            backdrop: "backdrop",
            close: "close",
            esc: "esc",
            timer: "timer"
        }),
        t = "SweetAlert2:",
        o = e => e.charAt(0).toUpperCase() + e.slice(1),
        s = e => Array.prototype.slice.call(e),
        a = e => {
            console.warn("".concat(t, " ").concat("object" == typeof e ? e.join(" ") : e))
        },
        r = e => {
            console.error("".concat(t, " ").concat(e))
        },
        n = [],
        i = (e, t) => {
            t = '"'.concat(e, '" is deprecated and will be removed in the next major release. Please use "').concat(t, '" instead.'), n.includes(t) || (n.push(t), a(t))
        },
        d = e => "function" == typeof e ? e() : e,
        c = e => e && "function" == typeof e.toPromise,
        l = e => c(e) ? e.toPromise() : Promise.resolve(e),
        p = e => e && Promise.resolve(e) === e,
        m = e => "object" == typeof e && e.jquery,
        g = e => e instanceof Element || m(e);
    var e = e => {
        const t = {};
        for (const n in e) t[e[n]] = "swal2-" + e[n];
        return t
    };
    const h = e(["container", "shown", "height-auto", "iosfix", "popup", "modal", "no-backdrop", "no-transition", "toast", "toast-shown", "show", "hide", "close", "title", "html-container", "actions", "confirm", "deny", "cancel", "default-outline", "footer", "icon", "icon-content", "image", "input", "file", "range", "select", "radio", "checkbox", "label", "textarea", "inputerror", "input-label", "validation-message", "progress-steps", "active-progress-step", "progress-step", "progress-step-line", "loader", "loading", "styled", "top", "top-start", "top-end", "top-left", "top-right", "center", "center-start", "center-end", "center-left", "center-right", "bottom", "bottom-start", "bottom-end", "bottom-left", "bottom-right", "grow-row", "grow-column", "grow-fullscreen", "rtl", "timer-progress-bar", "timer-progress-bar-container", "scrollbar-measure", "icon-success", "icon-warning", "icon-info", "icon-question", "icon-error"]),
        f = e(["success", "warning", "info", "question", "error"]),
        b = () => document.body.querySelector(".".concat(h.container)),
        y = e => {
            const t = b();
            return t ? t.querySelector(e) : null
        },
        v = e => y(".".concat(e)),
        w = () => v(h.popup),
        C = () => v(h.icon),
        k = () => v(h.title),
        A = () => v(h["html-container"]),
        P = () => v(h.image),
        B = () => v(h["progress-steps"]),
        x = () => v(h["validation-message"]),
        E = () => y(".".concat(h.actions, " .").concat(h.confirm)),
        S = () => y(".".concat(h.actions, " .").concat(h.deny));
    const T = () => y(".".concat(h.loader)),
        L = () => y(".".concat(h.actions, " .").concat(h.cancel)),
        O = () => v(h.actions),
        j = () => v(h.footer),
        D = () => v(h["timer-progress-bar"]),
        M = () => v(h.close),
        I = () => {
            const e = s(w().querySelectorAll('[tabindex]:not([tabindex="-1"]):not([tabindex="0"])')).sort((e, t) => (e = parseInt(e.getAttribute("tabindex")), (t = parseInt(t.getAttribute("tabindex"))) < e ? 1 : e < t ? -1 : 0));
            var t = s(w().querySelectorAll('\n  a[href],\n  area[href],\n  input:not([disabled]),\n  select:not([disabled]),\n  textarea:not([disabled]),\n  button:not([disabled]),\n  iframe,\n  object,\n  embed,\n  [tabindex="0"],\n  [contenteditable],\n  audio[controls],\n  video[controls],\n  summary\n')).filter(e => "-1" !== e.getAttribute("tabindex"));
            return (t => {
                const n = [];
                for (let e = 0; e < t.length; e++) - 1 === n.indexOf(t[e]) && n.push(t[e]);
                return n
            })(e.concat(t)).filter(e => ee(e))
        },
        H = () => !q() && !document.body.classList.contains(h["no-backdrop"]),
        q = () => document.body.classList.contains(h["toast-shown"]);

    function V(e) {
        var t = 1 < arguments.length && void 0 !== arguments[1] && arguments[1];
        const n = D();
        ee(n) && (t && (n.style.transition = "none", n.style.width = "100%"), setTimeout(() => {
            n.style.transition = "width ".concat(e / 1e3, "s linear"), n.style.width = "0%"
        }, 10))
    }
    const N = {
            previousBodyPadding: null
        },
        U = (t, e) => {
            if (t.textContent = "", e) {
                const n = new DOMParser,
                    o = n.parseFromString(e, "text/html");
                s(o.querySelector("head").childNodes).forEach(e => {
                    t.appendChild(e)
                }), s(o.querySelector("body").childNodes).forEach(e => {
                    t.appendChild(e)
                })
            }
        },
        F = (t, e) => {
            if (!e) return !1;
            var n = e.split(/\s+/);
            for (let e = 0; e < n.length; e++)
                if (!t.classList.contains(n[e])) return !1;
            return !0
        },
        R = (e, t, n) => {
            var o, i;
            if (o = e, i = t, s(o.classList).forEach(e => {
                    Object.values(h).includes(e) || Object.values(f).includes(e) || Object.values(i.showClass).includes(e) || o.classList.remove(e)
                }), t.customClass && t.customClass[n]) {
                if ("string" != typeof t.customClass[n] && !t.customClass[n].forEach) return a("Invalid type of customClass.".concat(n, '! Expected string or iterable object, got "').concat(typeof t.customClass[n], '"'));
                K(e, t.customClass[n])
            }
        },
        z = (e, t) => {
            if (!t) return null;
            switch (t) {
                case "select":
                case "textarea":
                case "file":
                    return Z(e, h[t]);
                case "checkbox":
                    return e.querySelector(".".concat(h.checkbox, " input"));
                case "radio":
                    return e.querySelector(".".concat(h.radio, " input:checked")) || e.querySelector(".".concat(h.radio, " input:first-child"));
                case "range":
                    return e.querySelector(".".concat(h.range, " input"));
                default:
                    return Z(e, h.input)
            }
        },
        W = e => {
            var t;
            e.focus(), "file" !== e.type && (t = e.value, e.value = "", e.value = t)
        },
        _ = (e, t, n) => {
            e && t && (t = "string" == typeof t ? t.split(/\s+/).filter(Boolean) : t).forEach(t => {
                e.forEach ? e.forEach(e => {
                    n ? e.classList.add(t) : e.classList.remove(t)
                }) : n ? e.classList.add(t) : e.classList.remove(t)
            })
        },
        K = (e, t) => {
            _(e, t, !0)
        },
        Y = (e, t) => {
            _(e, t, !1)
        },
        Z = (t, n) => {
            for (let e = 0; e < t.childNodes.length; e++)
                if (F(t.childNodes[e], n)) return t.childNodes[e]
        },
        J = (e, t, n) => {
            (n = n === "".concat(parseInt(n)) ? parseInt(n) : n) || 0 === parseInt(n) ? e.style[t] = "number" == typeof n ? "".concat(n, "px") : n : e.style.removeProperty(t)
        },
        X = function (e) {
            e.style.display = 1 < arguments.length && void 0 !== arguments[1] ? arguments[1] : "flex"
        },
        $ = e => {
            e.style.display = "none"
        },
        G = (e, t, n, o) => {
            const i = e.querySelector(t);
            i && (i.style[n] = o)
        },
        Q = (e, t, n) => {
            t ? X(e, n) : $(e)
        },
        ee = e => !(!e || !(e.offsetWidth || e.offsetHeight || e.getClientRects().length)),
        te = () => !ee(E()) && !ee(S()) && !ee(L()),
        ne = e => !!(e.scrollHeight > e.clientHeight),
        oe = e => {
            const t = window.getComputedStyle(e);
            var n = parseFloat(t.getPropertyValue("animation-duration") || "0"),
                e = parseFloat(t.getPropertyValue("transition-duration") || "0");
            return 0 < n || 0 < e
        },
        ie = () => "undefined" == typeof window || "undefined" == typeof document,
        se = '\n <div aria-labelledby="'.concat(h.title, '" aria-describedby="').concat(h["html-container"], '" class="').concat(h.popup, '" tabindex="-1">\n   <button type="button" class="').concat(h.close, '"></button>\n   <ul class="').concat(h["progress-steps"], '"></ul>\n   <div class="').concat(h.icon, '"></div>\n   <img class="').concat(h.image, '" />\n   <h2 class="').concat(h.title, '" id="').concat(h.title, '"></h2>\n   <div class="').concat(h["html-container"], '" id="').concat(h["html-container"], '"></div>\n   <input class="').concat(h.input, '" />\n   <input type="file" class="').concat(h.file, '" />\n   <div class="').concat(h.range, '">\n     <input type="range" />\n     <output></output>\n   </div>\n   <select class="').concat(h.select, '"></select>\n   <div class="').concat(h.radio, '"></div>\n   <label for="').concat(h.checkbox, '" class="').concat(h.checkbox, '">\n     <input type="checkbox" />\n     <span class="').concat(h.label, '"></span>\n   </label>\n   <textarea class="').concat(h.textarea, '"></textarea>\n   <div class="').concat(h["validation-message"], '" id="').concat(h["validation-message"], '"></div>\n   <div class="').concat(h.actions, '">\n     <div class="').concat(h.loader, '"></div>\n     <button type="button" class="').concat(h.confirm, '"></button>\n     <button type="button" class="').concat(h.deny, '"></button>\n     <button type="button" class="').concat(h.cancel, '"></button>\n   </div>\n   <div class="').concat(h.footer, '"></div>\n   <div class="').concat(h["timer-progress-bar-container"], '">\n     <div class="').concat(h["timer-progress-bar"], '"></div>\n   </div>\n </div>\n').replace(/(^|\n)\s*/g, ""),
        ae = () => {
            on.isVisible() && on.resetValidationMessage()
        },
        re = e => {
            var t = (() => {
                const e = b();
                return !!e && (e.remove(), Y([document.documentElement, document.body], [h["no-backdrop"], h["toast-shown"], h["has-column"]]), !0)
            })();
            if (ie()) r("SweetAlert2 requires document to initialize");
            else {
                const n = document.createElement("div");
                n.className = h.container, t && K(n, h["no-transition"]), U(n, se);
                const o = "string" == typeof (t = e.target) ? document.querySelector(t) : t;
                o.appendChild(n), (e => {
                    const t = w();
                    t.setAttribute("role", e.toast ? "alert" : "dialog"), t.setAttribute("aria-live", e.toast ? "polite" : "assertive"), e.toast || t.setAttribute("aria-modal", "true")
                })(e), e = o, "rtl" === window.getComputedStyle(e).direction && K(b(), h.rtl), (() => {
                    const e = w(),
                        t = Z(e, h.input),
                        n = Z(e, h.file),
                        o = e.querySelector(".".concat(h.range, " input")),
                        i = e.querySelector(".".concat(h.range, " output")),
                        s = Z(e, h.select),
                        a = e.querySelector(".".concat(h.checkbox, " input")),
                        r = Z(e, h.textarea);
                    t.oninput = ae, n.onchange = ae, s.onchange = ae, a.onchange = ae, r.oninput = ae, o.oninput = () => {
                        ae(), i.value = o.value
                    }, o.onchange = () => {
                        ae(), o.nextSibling.value = o.value
                    }
                })()
            }
        },
        ce = (e, t) => {
            e instanceof HTMLElement ? t.appendChild(e) : "object" == typeof e ? ((e, t) => {
                if (e.jquery) le(t, e);
                else U(t, e.toString())
            })(e, t) : e && U(t, e)
        },
        le = (t, n) => {
            if (t.textContent = "", 0 in n)
                for (let e = 0; e in n; e++) t.appendChild(n[e].cloneNode(!0));
            else t.appendChild(n.cloneNode(!0))
        },
        ue = (() => {
            if (ie()) return !1;
            var e = document.createElement("div"),
                t = {
                    WebkitAnimation: "webkitAnimationEnd",
                    OAnimation: "oAnimationEnd oanimationend",
                    animation: "animationend"
                };
            for (const n in t)
                if (Object.prototype.hasOwnProperty.call(t, n) && void 0 !== e.style[n]) return t[n];
            return !1
        })(),
        de = (e, t) => {
            var n, o, i, s, a, r = O(),
                c = T();
            (t.showConfirmButton || t.showDenyButton || t.showCancelButton ? X : $)(r), R(r, t, "actions"), n = r, o = c, i = t, s = E(), a = S(), r = L(), pe(s, "confirm", i), pe(a, "deny", i), pe(r, "cancel", i),
                function (e, t, n, o) {
                    if (!o.buttonsStyling) return Y([e, t, n], h.styled);
                    K([e, t, n], h.styled), o.confirmButtonColor && (e.style.backgroundColor = o.confirmButtonColor, K(e, h["default-outline"]));
                    o.denyButtonColor && (t.style.backgroundColor = o.denyButtonColor, K(t, h["default-outline"]));
                    o.cancelButtonColor && (n.style.backgroundColor = o.cancelButtonColor, K(n, h["default-outline"]))
                }(s, a, r, i), i.reverseButtons && (i.toast ? (n.insertBefore(r, s), n.insertBefore(a, s)) : (n.insertBefore(r, o), n.insertBefore(a, o), n.insertBefore(s, o))), U(c, t.loaderHtml), R(c, t, "loader")
        };

    function pe(e, t, n) {
        Q(e, n["show".concat(o(t), "Button")], "inline-block"), U(e, n["".concat(t, "ButtonText")]), e.setAttribute("aria-label", n["".concat(t, "ButtonAriaLabel")]), e.className = h[t], R(e, n, "".concat(t, "Button")), K(e, n["".concat(t, "ButtonClass")])
    }
    const me = (e, t) => {
        var n, o, i = b();
        i && (o = i, "string" == typeof (n = t.backdrop) ? o.style.background = n : n || K([document.documentElement, document.body], h["no-backdrop"]), o = i, (n = t.position) in h ? K(o, h[n]) : (a('The "position" parameter is not valid, defaulting to "center"'), K(o, h.center)), n = i, !(o = t.grow) || "string" != typeof o || (o = "grow-".concat(o)) in h && K(n, h[o]), R(i, t, "container"))
    };
    var ge = {
        awaitingPromise: new WeakMap,
        promise: new WeakMap,
        innerParams: new WeakMap,
        domCache: new WeakMap
    };
    const he = ["input", "file", "range", "select", "radio", "checkbox", "textarea"],
        fe = (e, o) => {
            const i = w();
            e = ge.innerParams.get(e);
            const s = !e || o.input !== e.input;
            he.forEach(e => {
                var t = h[e];
                const n = Z(i, t);
                ((e, t) => {
                    const n = z(w(), e);
                    if (n) {
                        be(n);
                        for (const o in t) n.setAttribute(o, t[o])
                    }
                })(e, o.inputAttributes), n.className = t, s && $(n)
            }), o.input && (s && (e => {
                if (!Ce[e.input]) return r('Unexpected type of input! Expected "text", "email", "password", "number", "tel", "select", "radio", "checkbox", "textarea", "file" or "url", got "'.concat(e.input, '"'));
                const t = we(e.input),
                    n = Ce[e.input](t, e);
                X(n), setTimeout(() => {
                    W(n)
                })
            })(o), (e => {
                const t = we(e.input);
                if (e.customClass) K(t, e.customClass.input)
            })(o))
        },
        be = t => {
            for (let e = 0; e < t.attributes.length; e++) {
                var n = t.attributes[e].name;
                ["type", "value", "style"].includes(n) || t.removeAttribute(n)
            }
        },
        ye = (e, t) => {
            e.placeholder && !t.inputPlaceholder || (e.placeholder = t.inputPlaceholder)
        },
        ve = (e, t, n) => {
            if (n.inputLabel) {
                e.id = h.input;
                const i = document.createElement("label");
                var o = h["input-label"];
                i.setAttribute("for", e.id), i.className = o, K(i, n.customClass.inputLabel), i.innerText = n.inputLabel, t.insertAdjacentElement("beforebegin", i)
            }
        },
        we = e => {
            e = h[e] || h.input;
            return Z(w(), e)
        },
        Ce = {};
    Ce.text = Ce.email = Ce.password = Ce.number = Ce.tel = Ce.url = (e, t) => ("string" == typeof t.inputValue || "number" == typeof t.inputValue ? e.value = t.inputValue : p(t.inputValue) || a('Unexpected type of inputValue! Expected "string", "number" or "Promise", got "'.concat(typeof t.inputValue, '"')), ve(e, e, t), ye(e, t), e.type = t.input, e), Ce.file = (e, t) => (ve(e, e, t), ye(e, t), e), Ce.range = (e, t) => {
        const n = e.querySelector("input"),
            o = e.querySelector("output");
        return n.value = t.inputValue, n.type = t.input, o.value = t.inputValue, ve(n, e, t), e
    }, Ce.select = (e, t) => {
        if (e.textContent = "", t.inputPlaceholder) {
            const n = document.createElement("option");
            U(n, t.inputPlaceholder), n.value = "", n.disabled = !0, n.selected = !0, e.appendChild(n)
        }
        return ve(e, e, t), e
    }, Ce.radio = e => (e.textContent = "", e), Ce.checkbox = (e, t) => {
        const n = z(w(), "checkbox");
        n.value = 1, n.id = h.checkbox, n.checked = Boolean(t.inputValue);
        var o = e.querySelector("span");
        return U(o, t.inputPlaceholder), e
    }, Ce.textarea = (n, e) => {
        n.value = e.inputValue, ye(n, e), ve(n, n, e);
        return setTimeout(() => {
            if ("MutationObserver" in window) {
                const t = parseInt(window.getComputedStyle(w()).width);
                new MutationObserver(() => {
                    var e, e = n.offsetWidth + (e = n, parseInt(window.getComputedStyle(e).marginLeft) + parseInt(window.getComputedStyle(e).marginRight));
                    e > t ? w().style.width = "".concat(e, "px") : w().style.width = null
                }).observe(n, {
                    attributes: !0,
                    attributeFilter: ["style"]
                })
            }
        }), n
    };
    const ke = (e, t) => {
            const n = A();
            R(n, t, "htmlContainer"), t.html ? (ce(t.html, n), X(n, "block")) : t.text ? (n.textContent = t.text, X(n, "block")) : $(n), fe(e, t)
        },
        Ae = (e, t) => {
            var n = j();
            Q(n, t.footer), t.footer && ce(t.footer, n), R(n, t, "footer")
        },
        Pe = (e, t) => {
            const n = M();
            U(n, t.closeButtonHtml), R(n, t, "closeButton"), Q(n, t.showCloseButton), n.setAttribute("aria-label", t.closeButtonAriaLabel)
        },
        Be = (e, t) => {
            var n = ge.innerParams.get(e),
                e = C();
            return n && t.icon === n.icon ? (Se(e, t), void xe(e, t)) : t.icon || t.iconHtml ? t.icon && -1 === Object.keys(f).indexOf(t.icon) ? (r('Unknown icon! Expected "success", "error", "warning", "info" or "question", got "'.concat(t.icon, '"')), $(e)) : (X(e), Se(e, t), xe(e, t), void K(e, t.showClass.icon)) : $(e)
        },
        xe = (e, t) => {
            for (const n in f) t.icon !== n && Y(e, f[n]);
            K(e, f[t.icon]), Te(e, t), Ee(), R(e, t, "icon")
        },
        Ee = () => {
            const e = w();
            var t = window.getComputedStyle(e).getPropertyValue("background-color");
            const n = e.querySelectorAll("[class^=swal2-success-circular-line], .swal2-success-fix");
            for (let e = 0; e < n.length; e++) n[e].style.backgroundColor = t
        },
        Se = (e, t) => {
            var n;
            e.textContent = "", t.iconHtml ? U(e, Le(t.iconHtml)) : "success" === t.icon ? U(e, '\n      <div class="swal2-success-circular-line-left"></div>\n      <span class="swal2-success-line-tip"></span> <span class="swal2-success-line-long"></span>\n      <div class="swal2-success-ring"></div> <div class="swal2-success-fix"></div>\n      <div class="swal2-success-circular-line-right"></div>\n    ') : "error" === t.icon ? U(e, '\n      <span class="swal2-x-mark">\n        <span class="swal2-x-mark-line-left"></span>\n        <span class="swal2-x-mark-line-right"></span>\n      </span>\n    ') : (n = {
                question: "?",
                warning: "!",
                info: "i"
            }, U(e, Le(n[t.icon])))
        },
        Te = (e, t) => {
            if (t.iconColor) {
                e.style.color = t.iconColor, e.style.borderColor = t.iconColor;
                for (const n of [".swal2-success-line-tip", ".swal2-success-line-long", ".swal2-x-mark-line-left", ".swal2-x-mark-line-right"]) G(e, n, "backgroundColor", t.iconColor);
                G(e, ".swal2-success-ring", "borderColor", t.iconColor)
            }
        },
        Le = e => '<div class="'.concat(h["icon-content"], '">').concat(e, "</div>"),
        Oe = (e, t) => {
            const n = P();
            if (!t.imageUrl) return $(n);
            X(n, ""), n.setAttribute("src", t.imageUrl), n.setAttribute("alt", t.imageAlt), J(n, "width", t.imageWidth), J(n, "height", t.imageHeight), n.className = h.image, R(n, t, "image")
        },
        je = (e, o) => {
            const i = B();
            if (!o.progressSteps || 0 === o.progressSteps.length) return $(i);
            X(i), i.textContent = "", o.currentProgressStep >= o.progressSteps.length && a("Invalid currentProgressStep parameter, it should be less than progressSteps.length (currentProgressStep like JS arrays starts from 0)"), o.progressSteps.forEach((e, t) => {
                var n, e = (n = e, e = document.createElement("li"), K(e, h["progress-step"]), U(e, n), e);
                i.appendChild(e), t === o.currentProgressStep && K(e, h["active-progress-step"]), t !== o.progressSteps.length - 1 && (t = (e => {
                    const t = document.createElement("li");
                    return K(t, h["progress-step-line"]), e.progressStepsDistance && (t.style.width = e.progressStepsDistance), t
                })(o), i.appendChild(t))
            })
        },
        De = (e, t) => {
            const n = k();
            Q(n, t.title || t.titleText, "block"), t.title && ce(t.title, n), t.titleText && (n.innerText = t.titleText), R(n, t, "title")
        },
        Me = (e, t) => {
            var n = b();
            const o = w();
            t.toast ? (J(n, "width", t.width), o.style.width = "100%", o.insertBefore(T(), C())) : J(o, "width", t.width), J(o, "padding", t.padding), t.background && (o.style.background = t.background), $(x()), ((e, t) => {
                if (e.className = "".concat(h.popup, " ").concat(ee(e) ? t.showClass.popup : ""), t.toast) {
                    K([document.documentElement, document.body], h["toast-shown"]);
                    K(e, h.toast)
                } else K(e, h.modal);
                if (R(e, t, "popup"), typeof t.customClass === "string") K(e, t.customClass);
                if (t.icon) K(e, h["icon-".concat(t.icon)])
            })(o, t)
        },
        Ie = (e, t) => {
            Me(e, t), me(e, t), je(e, t), Be(e, t), Oe(e, t), De(e, t), Pe(e, t), ke(e, t), de(e, t), Ae(e, t), "function" == typeof t.didRender && t.didRender(w())
        };
    const He = () => E() && E().click();
    const qe = e => {
            let t = w();
            t || on.fire(), t = w();
            var n = T();
            q() ? $(C()) : ((e, t) => {
                const n = O(),
                    o = T();
                if (!t && ee(E())) t = E();
                if (X(n), t) {
                    $(t);
                    o.setAttribute("data-button-to-replace", t.className)
                }
                o.parentNode.insertBefore(o, t), K([e, n], h.loading)
            })(t, e), X(n), t.setAttribute("data-loading", !0), t.setAttribute("aria-busy", !0), t.focus()
        },
        Ve = 100,
        Ne = {},
        Ue = () => {
            Ne.previousActiveElement && Ne.previousActiveElement.focus ? (Ne.previousActiveElement.focus(), Ne.previousActiveElement = null) : document.body && document.body.focus()
        },
        Fe = o => new Promise(e => {
            if (!o) return e();
            var t = window.scrollX,
                n = window.scrollY;
            Ne.restoreFocusTimeout = setTimeout(() => {
                Ue(), e()
            }, Ve), window.scrollTo(t, n)
        });
    const Re = () => {
            if (Ne.timeout) return (() => {
                const e = D();
                var t = parseInt(window.getComputedStyle(e).width);
                e.style.removeProperty("transition"), e.style.width = "100%";
                var n = parseInt(window.getComputedStyle(e).width),
                    n = parseInt(t / n * 100);
                e.style.removeProperty("transition"), e.style.width = "".concat(n, "%")
            })(), Ne.timeout.stop()
        },
        ze = () => {
            if (Ne.timeout) {
                var e = Ne.timeout.start();
                return V(e), e
            }
        };
    let We = !1;
    const _e = {};
    const Ke = t => {
            for (let e = t.target; e && e !== document; e = e.parentNode)
                for (const o in _e) {
                    var n = e.getAttribute(o);
                    if (n) return void _e[o].fire({
                        template: n
                    })
                }
        },
        Ye = {
            title: "",
            titleText: "",
            text: "",
            html: "",
            footer: "",
            icon: void 0,
            iconColor: void 0,
            iconHtml: void 0,
            template: void 0,
            toast: !1,
            showClass: {
                popup: "swal2-show",
                backdrop: "swal2-backdrop-show",
                icon: "swal2-icon-show"
            },
            hideClass: {
                popup: "swal2-hide",
                backdrop: "swal2-backdrop-hide",
                icon: "swal2-icon-hide"
            },
            customClass: {},
            target: "body",
            backdrop: !0,
            heightAuto: !0,
            allowOutsideClick: !0,
            allowEscapeKey: !0,
            allowEnterKey: !0,
            stopKeydownPropagation: !0,
            keydownListenerCapture: !1,
            showConfirmButton: !0,
            showDenyButton: !1,
            showCancelButton: !1,
            preConfirm: void 0,
            preDeny: void 0,
            confirmButtonText: "OK",
            confirmButtonAriaLabel: "",
            confirmButtonColor: void 0,
            denyButtonText: "No",
            denyButtonAriaLabel: "",
            denyButtonColor: void 0,
            cancelButtonText: "Cancel",
            cancelButtonAriaLabel: "",
            cancelButtonColor: void 0,
            buttonsStyling: !0,
            reverseButtons: !1,
            focusConfirm: !0,
            focusDeny: !1,
            focusCancel: !1,
            returnFocus: !0,
            showCloseButton: !1,
            closeButtonHtml: "&times;",
            closeButtonAriaLabel: "Close this dialog",
            loaderHtml: "",
            showLoaderOnConfirm: !1,
            showLoaderOnDeny: !1,
            imageUrl: void 0,
            imageWidth: void 0,
            imageHeight: void 0,
            imageAlt: "",
            timer: void 0,
            timerProgressBar: !1,
            width: void 0,
            padding: void 0,
            background: void 0,
            input: void 0,
            inputPlaceholder: "",
            inputLabel: "",
            inputValue: "",
            inputOptions: {},
            inputAutoTrim: !0,
            inputAttributes: {},
            inputValidator: void 0,
            returnInputValueOnDeny: !1,
            validationMessage: void 0,
            grow: !1,
            position: "center",
            progressSteps: [],
            currentProgressStep: void 0,
            progressStepsDistance: void 0,
            willOpen: void 0,
            didOpen: void 0,
            didRender: void 0,
            willClose: void 0,
            didClose: void 0,
            didDestroy: void 0,
            scrollbarPadding: !0
        },
        Ze = ["allowEscapeKey", "allowOutsideClick", "background", "buttonsStyling", "cancelButtonAriaLabel", "cancelButtonColor", "cancelButtonText", "closeButtonAriaLabel", "closeButtonHtml", "confirmButtonAriaLabel", "confirmButtonColor", "confirmButtonText", "currentProgressStep", "customClass", "denyButtonAriaLabel", "denyButtonColor", "denyButtonText", "didClose", "didDestroy", "footer", "hideClass", "html", "icon", "iconColor", "iconHtml", "imageAlt", "imageHeight", "imageUrl", "imageWidth", "preConfirm", "preDeny", "progressSteps", "returnFocus", "reverseButtons", "showCancelButton", "showCloseButton", "showConfirmButton", "showDenyButton", "text", "title", "titleText", "willClose"],
        Je = {},
        Xe = ["allowOutsideClick", "allowEnterKey", "backdrop", "focusConfirm", "focusDeny", "focusCancel", "returnFocus", "heightAuto", "keydownListenerCapture"],
        $e = e => Object.prototype.hasOwnProperty.call(Ye, e);
    const Ge = e => Je[e],
        Qe = e => {
            $e(e) || a('Unknown parameter "'.concat(e, '"'))
        },
        et = e => {
            Xe.includes(e) && a('The parameter "'.concat(e, '" is incompatible with toasts'))
        },
        tt = e => {
            Ge(e) && i(e, Ge(e))
        };
    var nt = Object.freeze({
        isValidParameter: $e,
        isUpdatableParameter: e => -1 !== Ze.indexOf(e),
        isDeprecatedParameter: Ge,
        argsToParams: n => {
            const o = {};
            return "object" != typeof n[0] || g(n[0]) ? ["title", "html", "icon"].forEach((e, t) => {
                t = n[t];
                "string" == typeof t || g(t) ? o[e] = t : void 0 !== t && r("Unexpected type of ".concat(e, '! Expected "string" or "Element", got ').concat(typeof t))
            }) : Object.assign(o, n[0]), o
        },
        isVisible: () => ee(w()),
        clickConfirm: He,
        clickDeny: () => S() && S().click(),
        clickCancel: () => L() && L().click(),
        getContainer: b,
        getPopup: w,
        getTitle: k,
        getHtmlContainer: A,
        getImage: P,
        getIcon: C,
        getInputLabel: () => v(h["input-label"]),
        getCloseButton: M,
        getActions: O,
        getConfirmButton: E,
        getDenyButton: S,
        getCancelButton: L,
        getLoader: T,
        getFooter: j,
        getTimerProgressBar: D,
        getFocusableElements: I,
        getValidationMessage: x,
        isLoading: () => w().hasAttribute("data-loading"),
        fire: function () {
            for (var e = arguments.length, t = new Array(e), n = 0; n < e; n++) t[n] = arguments[n];
            return new this(...t)
        },
        mixin: function (n) {
            class e extends this {
                _main(e, t) {
                    return super._main(e, Object.assign({}, n, t))
                }
            }
            return e
        },
        showLoading: qe,
        enableLoading: qe,
        getTimerLeft: () => Ne.timeout && Ne.timeout.getTimerLeft(),
        stopTimer: Re,
        resumeTimer: ze,
        toggleTimer: () => {
            var e = Ne.timeout;
            return e && (e.running ? Re : ze)()
        },
        increaseTimer: e => {
            if (Ne.timeout) {
                e = Ne.timeout.increase(e);
                return V(e, !0), e
            }
        },
        isTimerRunning: () => Ne.timeout && Ne.timeout.isRunning(),
        bindClickHandler: function () {
            var e = 0 < arguments.length && void 0 !== arguments[0] ? arguments[0] : "data-swal-template";
            _e[e] = this, We || (document.body.addEventListener("click", Ke), We = !0)
        }
    });

    function ot() {
        var e = ge.innerParams.get(this);
        if (e) {
            const t = ge.domCache.get(this);
            $(t.loader), q() ? e.icon && X(C()) : (e => {
                const t = e.popup.getElementsByClassName(e.loader.getAttribute("data-button-to-replace"));
                if (t.length) X(t[0], "inline-block");
                else if (te()) $(e.actions)
            })(t), Y([t.popup, t.actions], h.loading), t.popup.removeAttribute("aria-busy"), t.popup.removeAttribute("data-loading"), t.confirmButton.disabled = !1, t.denyButton.disabled = !1, t.cancelButton.disabled = !1
        }
    }
    const it = () => {
            null === N.previousBodyPadding && document.body.scrollHeight > window.innerHeight && (N.previousBodyPadding = parseInt(window.getComputedStyle(document.body).getPropertyValue("padding-right")), document.body.style.paddingRight = "".concat(N.previousBodyPadding + (() => {
                const e = document.createElement("div");
                e.className = h["scrollbar-measure"], document.body.appendChild(e);
                var t = e.getBoundingClientRect().width - e.clientWidth;
                return document.body.removeChild(e), t
            })(), "px"))
        },
        st = () => {
            null !== N.previousBodyPadding && (document.body.style.paddingRight = "".concat(N.previousBodyPadding, "px"), N.previousBodyPadding = null)
        },
        at = () => {
            var e;
            (/iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream || "MacIntel" === navigator.platform && 1 < navigator.maxTouchPoints) && !F(document.body, h.iosfix) && (e = document.body.scrollTop, document.body.style.top = "".concat(-1 * e, "px"), K(document.body, h.iosfix), (() => {
                const e = b();
                let t;
                e.ontouchstart = e => {
                    t = rt(e)
                }, e.ontouchmove = e => {
                    if (t) {
                        e.preventDefault();
                        e.stopPropagation()
                    }
                }
            })(), (() => {
                const e = !navigator.userAgent.match(/(CriOS|FxiOS|EdgiOS|YaBrowser|UCBrowser)/i);
                if (e) {
                    const t = 44;
                    if (w().scrollHeight > window.innerHeight - t) b().style.paddingBottom = "".concat(t, "px")
                }
            })())
        },
        rt = e => {
            var t, n = e.target,
                o = b();
            return !((t = e).touches && t.touches.length && "stylus" === t.touches[0].touchType || (e = e).touches && 1 < e.touches.length) && (n === o || !(ne(o) || "INPUT" === n.tagName || "TEXTAREA" === n.tagName || ne(A()) && A().contains(n)))
        },
        ct = () => {
            var e;
            F(document.body, h.iosfix) && (e = parseInt(document.body.style.top, 10), Y(document.body, h.iosfix), document.body.style.top = "", document.body.scrollTop = -1 * e)
        },
        lt = () => {
            const e = s(document.body.children);
            e.forEach(e => {
                e.hasAttribute("data-previous-aria-hidden") ? (e.setAttribute("aria-hidden", e.getAttribute("data-previous-aria-hidden")), e.removeAttribute("data-previous-aria-hidden")) : e.removeAttribute("aria-hidden")
            })
        };
    var ut = {
        swalPromiseResolve: new WeakMap,
        swalPromiseReject: new WeakMap
    };

    function dt(e, t, n, o) {
        q() ? ht(e, o) : (Fe(n).then(() => ht(e, o)), Ne.keydownTarget.removeEventListener("keydown", Ne.keydownHandler, {
            capture: Ne.keydownListenerCapture
        }), Ne.keydownHandlerAdded = !1), /^((?!chrome|android).)*safari/i.test(navigator.userAgent) ? (t.setAttribute("style", "display:none !important"), t.removeAttribute("class"), t.innerHTML = "") : t.remove(), H() && (st(), ct(), lt()), Y([document.documentElement, document.body], [h.shown, h["height-auto"], h["no-backdrop"], h["toast-shown"]])
    }

    function pt(e) {
        e = void 0 !== (n = e) ? Object.assign({
            isConfirmed: !1,
            isDenied: !1,
            isDismissed: !1
        }, n) : {
            isConfirmed: !1,
            isDenied: !1,
            isDismissed: !0
        };
        const t = ut.swalPromiseResolve.get(this);
        var n = (e => {
            const t = w();
            if (!t) return false;
            const n = ge.innerParams.get(e);
            if (!n || F(t, n.hideClass.popup)) return false;
            Y(t, n.showClass.popup), K(t, n.hideClass.popup);
            const o = b();
            return Y(o, n.showClass.backdrop), K(o, n.hideClass.backdrop), gt(e, t, n), true
        })(this);
        this.isAwaitingPromise() ? e.isDismissed || (mt(this), t(e)) : n && t(e)
    }
    const mt = e => {
            e.isAwaitingPromise() && (ge.awaitingPromise.delete(e), ge.innerParams.get(e) || e._destroy())
        },
        gt = (e, t, n) => {
            var o, i, s, a = b(),
                r = ue && oe(t);
            "function" == typeof n.willClose && n.willClose(t), r ? (o = e, i = t, s = a, r = n.returnFocus, t = n.didClose, Ne.swalCloseEventFinishedCallback = dt.bind(null, o, s, r, t), i.addEventListener(ue, function (e) {
                e.target === i && (Ne.swalCloseEventFinishedCallback(), delete Ne.swalCloseEventFinishedCallback)
            })) : dt(e, a, n.returnFocus, n.didClose)
        },
        ht = (e, t) => {
            setTimeout(() => {
                "function" == typeof t && t.bind(e.params)(), e._destroy()
            })
        };

    function ft(e, t, n) {
        const o = ge.domCache.get(e);
        t.forEach(e => {
            o[e].disabled = n
        })
    }

    function bt(e, t) {
        if (!e) return !1;
        if ("radio" === e.type) {
            const n = e.parentNode.parentNode,
                o = n.querySelectorAll("input");
            for (let e = 0; e < o.length; e++) o[e].disabled = t
        } else e.disabled = t
    }
    class yt {
        constructor(e, t) {
            this.callback = e, this.remaining = t, this.running = !1, this.start()
        }
        start() {
            return this.running || (this.running = !0, this.started = new Date, this.id = setTimeout(this.callback, this.remaining)), this.remaining
        }
        stop() {
            return this.running && (this.running = !1, clearTimeout(this.id), this.remaining -= new Date - this.started), this.remaining
        }
        increase(e) {
            var t = this.running;
            return t && this.stop(), this.remaining += e, t && this.start(), this.remaining
        }
        getTimerLeft() {
            return this.running && (this.stop(), this.start()), this.remaining
        }
        isRunning() {
            return this.running
        }
    }
    var vt = {
        email: (e, t) => /^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9.-]+\.[a-zA-Z0-9-]{2,24}$/.test(e) ? Promise.resolve() : Promise.resolve(t || "Invalid email address"),
        url: (e, t) => /^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-z]{2,63}\b([-a-zA-Z0-9@:%_+.~#?&/=]*)$/.test(e) ? Promise.resolve() : Promise.resolve(t || "Invalid URL")
    };

    function wt(e) {
        var t, n;
        (t = e).inputValidator || Object.keys(vt).forEach(e => {
            t.input === e && (t.inputValidator = vt[e])
        }), e.showLoaderOnConfirm && !e.preConfirm && a("showLoaderOnConfirm is set to true, but preConfirm is not defined.\nshowLoaderOnConfirm should be used together with preConfirm, see usage example:\nhttps://sweetalert2.github.io/#ajax-request"), (n = e).target && ("string" != typeof n.target || document.querySelector(n.target)) && ("string" == typeof n.target || n.target.appendChild) || (a('Target parameter is not valid, defaulting to "body"'), n.target = "body"), "string" == typeof e.title && (e.title = e.title.split("\n").join("<br />")), re(e)
    }
    const Ct = ["swal-title", "swal-html", "swal-footer"],
        kt = e => {
            e = "string" == typeof e.template ? document.querySelector(e.template) : e.template;
            if (!e) return {};
            e = e.content;
            return (e => {
                const n = Ct.concat(["swal-param", "swal-button", "swal-image", "swal-icon", "swal-input", "swal-input-option"]);
                s(e.children).forEach(e => {
                    const t = e.tagName.toLowerCase();
                    if (n.indexOf(t) === -1) a("Unrecognized element <".concat(t, ">"))
                })
            })(e), Object.assign((e => {
                const o = {};
                return s(e.querySelectorAll("swal-param")).forEach(e => {
                    At(e, ["name", "value"]);
                    const t = e.getAttribute("name");
                    let n = e.getAttribute("value");
                    if (typeof Ye[t] === "boolean" && n === "false") n = false;
                    if (typeof Ye[t] === "object") n = JSON.parse(n);
                    o[t] = n
                }), o
            })(e), (e => {
                const n = {};
                return s(e.querySelectorAll("swal-button")).forEach(e => {
                    At(e, ["type", "color", "aria-label"]);
                    const t = e.getAttribute("type");
                    n["".concat(t, "ButtonText")] = e.innerHTML;
                    n["show".concat(o(t), "Button")] = true;
                    if (e.hasAttribute("color")) n["".concat(t, "ButtonColor")] = e.getAttribute("color");
                    if (e.hasAttribute("aria-label")) n["".concat(t, "ButtonAriaLabel")] = e.getAttribute("aria-label")
                }), n
            })(e), (e => {
                const t = {},
                    n = e.querySelector("swal-image");
                if (n) {
                    At(n, ["src", "width", "height", "alt"]);
                    if (n.hasAttribute("src")) t.imageUrl = n.getAttribute("src");
                    if (n.hasAttribute("width")) t.imageWidth = n.getAttribute("width");
                    if (n.hasAttribute("height")) t.imageHeight = n.getAttribute("height");
                    if (n.hasAttribute("alt")) t.imageAlt = n.getAttribute("alt")
                }
                return t
            })(e), (e => {
                const t = {},
                    n = e.querySelector("swal-icon");
                if (n) {
                    At(n, ["type", "color"]);
                    if (n.hasAttribute("type")) t.icon = n.getAttribute("type");
                    if (n.hasAttribute("color")) t.iconColor = n.getAttribute("color");
                    t.iconHtml = n.innerHTML
                }
                return t
            })(e), (e => {
                const o = {},
                    t = e.querySelector("swal-input");
                if (t) {
                    At(t, ["type", "label", "placeholder", "value"]);
                    o.input = t.getAttribute("type") || "text";
                    if (t.hasAttribute("label")) o.inputLabel = t.getAttribute("label");
                    if (t.hasAttribute("placeholder")) o.inputPlaceholder = t.getAttribute("placeholder");
                    if (t.hasAttribute("value")) o.inputValue = t.getAttribute("value")
                }
                const n = e.querySelectorAll("swal-input-option");
                if (n.length) {
                    o.inputOptions = {};
                    s(n).forEach(e => {
                        At(e, ["value"]);
                        const t = e.getAttribute("value");
                        const n = e.innerHTML;
                        o.inputOptions[t] = n
                    })
                }
                return o
            })(e), ((e, t) => {
                const n = {};
                for (const o in t) {
                    const i = t[o];
                    const s = e.querySelector(i);
                    if (s) {
                        At(s, []);
                        n[i.replace(/^swal-/, "")] = s.innerHTML.trim()
                    }
                }
                return n
            })(e, Ct))
        },
        At = (t, n) => {
            s(t.attributes).forEach(e => {
                -1 === n.indexOf(e.name) && a(['Unrecognized attribute "'.concat(e.name, '" on <').concat(t.tagName.toLowerCase(), ">."), "".concat(n.length ? "Allowed attributes are: ".concat(n.join(", ")) : "To set the value, use HTML within the element.")])
            })
        },
        Pt = 10,
        Bt = e => {
            const t = b(),
                n = w();
            "function" == typeof e.willOpen && e.willOpen(n);
            var o = window.getComputedStyle(document.body).overflowY;
            ((e, t, n) => {
                if (K(e, n.showClass.backdrop), t.style.setProperty("opacity", "0", "important"), X(t, "grid"), setTimeout(() => {
                        K(t, n.showClass.popup);
                        t.style.removeProperty("opacity")
                    }, Pt), K([document.documentElement, document.body], h.shown), n.heightAuto && n.backdrop && !n.toast) K([document.documentElement, document.body], h["height-auto"])
            })(t, n, e), setTimeout(() => {
                ((e, t) => {
                    if (ue && oe(t)) {
                        e.style.overflowY = "hidden";
                        t.addEventListener(ue, xt)
                    } else e.style.overflowY = "auto"
                })(t, n)
            }, Pt), H() && (((e, t, n) => {
                if (at(), t && n !== "hidden") it();
                setTimeout(() => {
                    e.scrollTop = 0
                })
            })(t, e.scrollbarPadding, o), (() => {
                const e = s(document.body.children);
                e.forEach(e => {
                    e === b() || e.contains(b()) || (e.hasAttribute("aria-hidden") && e.setAttribute("data-previous-aria-hidden", e.getAttribute("aria-hidden")), e.setAttribute("aria-hidden", "true"))
                })
            })()), q() || Ne.previousActiveElement || (Ne.previousActiveElement = document.activeElement), "function" == typeof e.didOpen && setTimeout(() => e.didOpen(n)), Y(t, h["no-transition"])
        },
        xt = e => {
            const t = w();
            if (e.target === t) {
                const n = b();
                t.removeEventListener(ue, xt), n.style.overflowY = "auto"
            }
        },
        Et = (e, t) => {
            "select" === t.input || "radio" === t.input ? ((t, n) => {
                const o = w(),
                    i = e => Tt[n.input](o, Lt(e), n);
                if (c(n.inputOptions) || p(n.inputOptions)) {
                    qe(E());
                    l(n.inputOptions).then(e => {
                        t.hideLoading();
                        i(e)
                    })
                } else if (typeof n.inputOptions === "object") i(n.inputOptions);
                else r("Unexpected type of inputOptions! Expected object, Map or Promise, got ".concat(typeof n.inputOptions))
            })(e, t) : ["text", "email", "number", "tel", "textarea"].includes(t.input) && (c(t.inputValue) || p(t.inputValue)) && (qe(E()), ((t, n) => {
                const o = t.getInput();
                $(o), l(n.inputValue).then(e => {
                    o.value = n.input === "number" ? parseFloat(e) || 0 : "".concat(e);
                    X(o);
                    o.focus();
                    t.hideLoading()
                }).catch(e => {
                    r("Error in inputValue promise: ".concat(e));
                    o.value = "";
                    X(o);
                    o.focus();
                    t.hideLoading()
                })
            })(e, t))
        },
        St = (e, t) => {
            const n = e.getInput();
            if (!n) return null;
            switch (t.input) {
                case "checkbox":
                    return n.checked ? 1 : 0;
                case "radio":
                    return (o = n).checked ? o.value : null;
                case "file":
                    return (o = n).files.length ? null !== o.getAttribute("multiple") ? o.files : o.files[0] : null;
                default:
                    return t.inputAutoTrim ? n.value.trim() : n.value
            }
            var o
        },
        Tt = {
            select: (e, t, i) => {
                const s = Z(e, h.select),
                    a = (e, t, n) => {
                        const o = document.createElement("option");
                        o.value = n, U(o, t), o.selected = Ot(n, i.inputValue), e.appendChild(o)
                    };
                t.forEach(e => {
                    var t = e[0];
                    const n = e[1];
                    if (Array.isArray(n)) {
                        const o = document.createElement("optgroup");
                        o.label = t, o.disabled = !1, s.appendChild(o), n.forEach(e => a(o, e[1], e[0]))
                    } else a(s, n, t)
                }), s.focus()
            },
            radio: (e, t, s) => {
                const a = Z(e, h.radio);
                t.forEach(e => {
                    var t = e[0],
                        e = e[1];
                    const n = document.createElement("input"),
                        o = document.createElement("label");
                    n.type = "radio", n.name = h.radio, n.value = t, Ot(t, s.inputValue) && (n.checked = !0);
                    const i = document.createElement("span");
                    U(i, e), i.className = h.label, o.appendChild(n), o.appendChild(i), a.appendChild(o)
                });
                const n = a.querySelectorAll("input");
                n.length && n[0].focus()
            }
        },
        Lt = n => {
            const o = [];
            return "undefined" != typeof Map && n instanceof Map ? n.forEach((e, t) => {
                let n = e;
                "object" == typeof n && (n = Lt(n)), o.push([t, n])
            }) : Object.keys(n).forEach(e => {
                let t = n[e];
                "object" == typeof t && (t = Lt(t)), o.push([e, t])
            }), o
        },
        Ot = (e, t) => t && t.toString() === e.toString(),
        jt = e => {
            var t = ge.innerParams.get(e);
            e.disableButtons(), t.input ? It(e, "confirm") : Ut(e, !0)
        },
        Dt = e => {
            var t = ge.innerParams.get(e);
            e.disableButtons(), t.returnInputValueOnDeny ? It(e, "deny") : qt(e, !1)
        },
        Mt = (e, t) => {
            e.disableButtons(), t(u.cancel)
        },
        It = (e, t) => {
            var n = ge.innerParams.get(e),
                o = St(e, n);
            n.inputValidator ? Ht(e, o, t) : e.getInput().checkValidity() ? ("deny" === t ? qt : Ut)(e, o) : (e.enableButtons(), e.showValidationMessage(n.validationMessage))
        },
        Ht = (t, n, o) => {
            const e = ge.innerParams.get(t);
            t.disableInput();
            const i = Promise.resolve().then(() => l(e.inputValidator(n, e.validationMessage)));
            i.then(e => {
                t.enableButtons(), t.enableInput(), e ? t.showValidationMessage(e) : ("deny" === o ? qt : Ut)(t, n)
            })
        },
        qt = (t, n) => {
            const e = ge.innerParams.get(t || void 0);
            if (e.showLoaderOnDeny && qe(S()), e.preDeny) {
                ge.awaitingPromise.set(t || void 0, !0);
                const o = Promise.resolve().then(() => l(e.preDeny(n, e.validationMessage)));
                o.then(e => {
                    !1 === e ? t.hideLoading() : t.closePopup({
                        isDenied: !0,
                        value: void 0 === e ? n : e
                    })
                }).catch(e => Nt(t || void 0, e))
            } else t.closePopup({
                isDenied: !0,
                value: n
            })
        },
        Vt = (e, t) => {
            e.closePopup({
                isConfirmed: !0,
                value: t
            })
        },
        Nt = (e, t) => {
            e.rejectPromise(t)
        },
        Ut = (t, n) => {
            const e = ge.innerParams.get(t || void 0);
            if (e.showLoaderOnConfirm && qe(), e.preConfirm) {
                t.resetValidationMessage(), ge.awaitingPromise.set(t || void 0, !0);
                const o = Promise.resolve().then(() => l(e.preConfirm(n, e.validationMessage)));
                o.then(e => {
                    ee(x()) || !1 === e ? t.hideLoading() : Vt(t, void 0 === e ? n : e)
                }).catch(e => Nt(t || void 0, e))
            } else Vt(t, n)
        },
        Ft = (t, e, n, o) => {
            e.keydownTarget && e.keydownHandlerAdded && (e.keydownTarget.removeEventListener("keydown", e.keydownHandler, {
                capture: e.keydownListenerCapture
            }), e.keydownHandlerAdded = !1), n.toast || (e.keydownHandler = e => ((e, t, n) => {
                const o = ge.innerParams.get(e);
                o && (o.stopKeydownPropagation && t.stopPropagation(), "Enter" === t.key ? _t(e, t, o) : "Tab" === t.key ? Kt(t, o) : [...zt, ...Wt].includes(t.key) ? Yt(t.key) : "Escape" === t.key && Zt(t, o, n))
            })(t, e, o), e.keydownTarget = n.keydownListenerCapture ? window : w(), e.keydownListenerCapture = n.keydownListenerCapture, e.keydownTarget.addEventListener("keydown", e.keydownHandler, {
                capture: e.keydownListenerCapture
            }), e.keydownHandlerAdded = !0)
        },
        Rt = (e, t, n) => {
            const o = I();
            if (o.length) return (t += n) === o.length ? t = 0 : -1 === t && (t = o.length - 1), o[t].focus();
            w().focus()
        },
        zt = ["ArrowRight", "ArrowDown"],
        Wt = ["ArrowLeft", "ArrowUp"],
        _t = (e, t, n) => {
            t.isComposing || t.target && e.getInput() && t.target.outerHTML === e.getInput().outerHTML && (["textarea", "file"].includes(n.input) || (He(), t.preventDefault()))
        },
        Kt = (e, t) => {
            var n = e.target,
                o = I();
            let i = -1;
            for (let e = 0; e < o.length; e++)
                if (n === o[e]) {
                    i = e;
                    break
                } e.shiftKey ? Rt(0, i, -1) : Rt(0, i, 1), e.stopPropagation(), e.preventDefault()
        },
        Yt = e => {
            const t = E(),
                n = S(),
                o = L();
            if ([t, n, o].includes(document.activeElement)) {
                e = zt.includes(e) ? "nextElementSibling" : "previousElementSibling";
                const i = document.activeElement[e];
                i && i.focus()
            }
        },
        Zt = (e, t, n) => {
            d(t.allowEscapeKey) && (e.preventDefault(), n(u.esc))
        },
        Jt = (e, t, n) => {
            var o, i, s, a, r, c, l;
            ge.innerParams.get(e).toast ? (c = e, l = n, t.popup.onclick = () => {
                var e = ge.innerParams.get(c);
                e.showConfirmButton || e.showDenyButton || e.showCancelButton || e.showCloseButton || e.timer || e.input || l(u.close)
            }) : ((r = t).popup.onmousedown = () => {
                r.container.onmouseup = function (e) {
                    r.container.onmouseup = void 0, e.target === r.container && (Xt = !0)
                }
            }, (a = t).container.onmousedown = () => {
                a.popup.onmouseup = function (e) {
                    a.popup.onmouseup = void 0, e.target !== a.popup && !a.popup.contains(e.target) || (Xt = !0)
                }
            }, o = e, s = n, (i = t).container.onclick = e => {
                var t = ge.innerParams.get(o);
                Xt ? Xt = !1 : e.target === i.container && d(t.allowOutsideClick) && s(u.backdrop)
            })
        };
    let Xt = !1;
    const $t = (e, t, n) => {
            var o = D();
            $(o), t.timer && (e.timeout = new yt(() => {
                n("timer"), delete e.timeout
            }, t.timer), t.timerProgressBar && (X(o), setTimeout(() => {
                e.timeout && e.timeout.running && V(t.timer)
            })))
        },
        Gt = (e, t) => {
            if (!t.toast) return d(t.allowEnterKey) ? void(((e, t) => {
                if (t.focusDeny && ee(e.denyButton)) {
                    e.denyButton.focus();
                    return true
                }
                if (t.focusCancel && ee(e.cancelButton)) {
                    e.cancelButton.focus();
                    return true
                }
                if (t.focusConfirm && ee(e.confirmButton)) {
                    e.confirmButton.focus();
                    return true
                }
                return false
            })(e, t) || Rt(0, -1, 1)) : (() => {
                if (document.activeElement && typeof document.activeElement.blur === "function") document.activeElement.blur()
            })()
        };
    const Qt = e => {
            e.isAwaitingPromise() ? (en(ge, e), ge.awaitingPromise.set(e, !0)) : (en(ut, e), en(ge, e))
        },
        en = (e, t) => {
            for (const n in e) e[n].delete(t)
        };
    e = Object.freeze({
        hideLoading: ot,
        disableLoading: ot,
        getInput: function (e) {
            var t = ge.innerParams.get(e || this);
            return (e = ge.domCache.get(e || this)) ? z(e.popup, t.input) : null
        },
        close: pt,
        isAwaitingPromise: function () {
            return !!ge.awaitingPromise.get(this)
        },
        rejectPromise: function (e) {
            const t = ut.swalPromiseReject.get(this);
            mt(this), t && t(e)
        },
        closePopup: pt,
        closeModal: pt,
        closeToast: pt,
        enableButtons: function () {
            ft(this, ["confirmButton", "denyButton", "cancelButton"], !1)
        },
        disableButtons: function () {
            ft(this, ["confirmButton", "denyButton", "cancelButton"], !0)
        },
        enableInput: function () {
            return bt(this.getInput(), !1)
        },
        disableInput: function () {
            return bt(this.getInput(), !0)
        },
        showValidationMessage: function (e) {
            const t = ge.domCache.get(this);
            var n = ge.innerParams.get(this);
            U(t.validationMessage, e), t.validationMessage.className = h["validation-message"], n.customClass && n.customClass.validationMessage && K(t.validationMessage, n.customClass.validationMessage), X(t.validationMessage);
            const o = this.getInput();
            o && (o.setAttribute("aria-invalid", !0), o.setAttribute("aria-describedby", h["validation-message"]), W(o), K(o, h.inputerror))
        },
        resetValidationMessage: function () {
            var e = ge.domCache.get(this);
            e.validationMessage && $(e.validationMessage);
            const t = this.getInput();
            t && (t.removeAttribute("aria-invalid"), t.removeAttribute("aria-describedby"), Y(t, h.inputerror))
        },
        getProgressSteps: function () {
            return ge.domCache.get(this).progressSteps
        },
        _main: function (e) {
            var t = 1 < arguments.length && void 0 !== arguments[1] ? arguments[1] : {};
            (e => {
                !e.backdrop && e.allowOutsideClick && a('"allowOutsideClick" parameter requires `backdrop` parameter to be set to `true`');
                for (const t in e) Qe(t), e.toast && et(t), tt(t)
            })(Object.assign({}, t, e)), Ne.currentInstance && (Ne.currentInstance._destroy(), H() && lt()), Ne.currentInstance = this, wt(e = ((e, t) => {
                const n = kt(e),
                    o = Object.assign({}, Ye, t, n, e);
                return o.showClass = Object.assign({}, Ye.showClass, o.showClass), o.hideClass = Object.assign({}, Ye.hideClass, o.hideClass), o
            })(e, t)), Object.freeze(e), Ne.timeout && (Ne.timeout.stop(), delete Ne.timeout), clearTimeout(Ne.restoreFocusTimeout);
            var o, i, s, t = (e => {
                const t = {
                    popup: w(),
                    container: b(),
                    actions: O(),
                    confirmButton: E(),
                    denyButton: S(),
                    cancelButton: L(),
                    loader: T(),
                    closeButton: M(),
                    validationMessage: x(),
                    progressSteps: B()
                };
                return ge.domCache.set(e, t), t
            })(this);
            return Ie(this, e), ge.innerParams.set(this, e), o = this, i = t, s = e, new Promise((e, t) => {
                const n = e => {
                    o.closePopup({
                        isDismissed: !0,
                        dismiss: e
                    })
                };
                ut.swalPromiseResolve.set(o, e), ut.swalPromiseReject.set(o, t), i.confirmButton.onclick = () => jt(o), i.denyButton.onclick = () => Dt(o), i.cancelButton.onclick = () => Mt(o, n), i.closeButton.onclick = () => n(u.close), Jt(o, i, n), Ft(o, Ne, s, n), Et(o, s), Bt(s), $t(Ne, s, n), Gt(i, s), setTimeout(() => {
                    i.container.scrollTop = 0
                })
            })
        },
        update: function (t) {
            var e = w(),
                n = ge.innerParams.get(this);
            if (!e || F(e, n.hideClass.popup)) return a("You're trying to update the closed or closing popup, that won't work. Use the update() method in preConfirm parameter or show a new popup.");
            const o = {};
            Object.keys(t).forEach(e => {
                on.isUpdatableParameter(e) ? o[e] = t[e] : a('Invalid parameter to update: "'.concat(e, '". Updatable params are listed here: https://github.com/sweetalert2/sweetalert2/blob/master/src/utils/params.js\n\nIf you think this parameter should be updatable, request it here: https://github.com/sweetalert2/sweetalert2/issues/new?template=02_feature_request.md'))
            }), n = Object.assign({}, n, o), Ie(this, n), ge.innerParams.set(this, n), Object.defineProperties(this, {
                params: {
                    value: Object.assign({}, this.params, t),
                    writable: !1,
                    enumerable: !0
                }
            })
        },
        _destroy: function () {
            var e = ge.domCache.get(this);
            const t = ge.innerParams.get(this);
            t ? (e.popup && Ne.swalCloseEventFinishedCallback && (Ne.swalCloseEventFinishedCallback(), delete Ne.swalCloseEventFinishedCallback), Ne.deferDisposalTimer && (clearTimeout(Ne.deferDisposalTimer), delete Ne.deferDisposalTimer), "function" == typeof t.didDestroy && t.didDestroy(), e = this, Qt(e), delete e.params, delete Ne.keydownHandler, delete Ne.keydownTarget, delete Ne.currentInstance) : Qt(this)
        }
    });
    let tn;
    class nn {
        constructor() {
            if ("undefined" != typeof window) {
                tn = this;
                for (var e = arguments.length, t = new Array(e), n = 0; n < e; n++) t[n] = arguments[n];
                var o = Object.freeze(this.constructor.argsToParams(t));
                Object.defineProperties(this, {
                    params: {
                        value: o,
                        writable: !1,
                        enumerable: !0,
                        configurable: !0
                    }
                });
                o = this._main(this.params);
                ge.promise.set(this, o)
            }
        }
        then(e) {
            const t = ge.promise.get(this);
            return t.then(e)
        } finally(e) {
            const t = ge.promise.get(this);
            return t.finally(e)
        }
    }
    Object.assign(nn.prototype, e), Object.assign(nn, nt), Object.keys(e).forEach(e => {
        nn[e] = function () {
            if (tn) return tn[e](...arguments)
        }
    }), nn.DismissReason = u, nn.version = "11.2.1";
    const on = nn;
    return on.default = on, on
}), void 0 !== this && this.Sweetalert2 && (this.swal = this.sweetAlert = this.Swal = this.SweetAlert = this.Sweetalert2);
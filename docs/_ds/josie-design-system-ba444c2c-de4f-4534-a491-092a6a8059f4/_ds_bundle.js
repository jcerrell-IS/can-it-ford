/* @ds-bundle: {"namespace":"JosieDesignSystem","components":[{"name":"Badge","sourcePath":"components/general/Badge/Badge.jsx"},{"name":"Button","sourcePath":"components/general/Button/Button.jsx"},{"name":"Card","sourcePath":"components/general/Card/Card.jsx"},{"name":"Input","sourcePath":"components/general/Input/Input.jsx"},{"name":"Stack","sourcePath":"components/general/Stack/Stack.jsx"}],"sourceHashes":{"components/general/Badge/Badge.jsx":"fd9aea1bbe60","components/general/Badge/Badge.d.ts":"55be4535c6bd","components/general/Badge/Badge.prompt.md":"8db4bb2be9e2","components/general/Button/Button.jsx":"29dcd84a3cc8","components/general/Button/Button.d.ts":"ffab58d8862c","components/general/Button/Button.prompt.md":"5119593c62a9","components/general/Card/Card.jsx":"a49c6d6f9a64","components/general/Card/Card.d.ts":"73d9402c8cd2","components/general/Card/Card.prompt.md":"68926086707a","components/general/Input/Input.jsx":"2c3e83ee40b5","components/general/Input/Input.d.ts":"305318892fdf","components/general/Input/Input.prompt.md":"cc238f5f0441","components/general/Stack/Stack.jsx":"2ce796858737","components/general/Stack/Stack.d.ts":"78e62f7da453","components/general/Stack/Stack.prompt.md":"dfa05658591c"},"inlinedExternals":[],"builtBy":"cc-design-sync"} */
"use strict";
var JosieDesignSystem = (() => {
  var __create = Object.create;
  var __defProp = Object.defineProperty;
  var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
  var __getOwnPropNames = Object.getOwnPropertyNames;
  var __getProtoOf = Object.getPrototypeOf;
  var __hasOwnProp = Object.prototype.hasOwnProperty;
  var __esm = (fn, res, err) => function __init() {
    if (err) throw err[0];
    try {
      return fn && (res = (0, fn[__getOwnPropNames(fn)[0]])(fn = 0)), res;
    } catch (e) {
      throw err = [e], e;
    }
  };
  var __commonJS = (cb, mod) => function __require() {
    try {
      return mod || (0, cb[__getOwnPropNames(cb)[0]])((mod = { exports: {} }).exports, mod), mod.exports;
    } catch (e) {
      throw mod = 0, e;
    }
  };
  var __export = (target, all) => {
    for (var name in all)
      __defProp(target, name, { get: all[name], enumerable: true });
  };
  var __copyProps = (to, from, except, desc) => {
    if (from && typeof from === "object" || typeof from === "function") {
      for (let key of __getOwnPropNames(from))
        if (!__hasOwnProp.call(to, key) && key !== except)
          __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
    }
    return to;
  };
  var __toESM = (mod, isNodeMode, target) => (target = mod != null ? __create(__getProtoOf(mod)) : {}, __copyProps(
    // If the importer is in node compatibility mode or this is not an ESM
    // file that has been converted to a CommonJS file using a Babel-
    // compatible transform (i.e. "__esModule" has not been set), then set
    // "default" to the CommonJS "module.exports" for node compatibility.
    isNodeMode || !mod || !mod.__esModule ? __defProp(target, "default", { value: mod, enumerable: true }) : target,
    mod
  ));
  var __toCommonJS = (mod) => __copyProps(__defProp({}, "__esModule", { value: true }), mod);

  // <define:import.meta.env>
  var init_define_import_meta_env = __esm({
    "<define:import.meta.env>"() {
    }
  });

  // shim:react-shim
  var require_react_shim = __commonJS({
    "shim:react-shim"(exports, module) {
      init_define_import_meta_env();
      var R = window.React;
      function np(p, k) {
        var o = {};
        for (var x in p) if (x !== "children") o[x] = p[x];
        if (k !== void 0) o.key = k;
        return o;
      }
      function jsx4(t, p, k) {
        var c = p && p.children;
        return c === void 0 ? R.createElement(t, np(p, k)) : R.createElement(t, np(p, k), c);
      }
      function jsxs5(t, p, k) {
        return R.createElement.apply(R, [t, np(p, k)].concat(p.children));
      }
      module.exports = R;
      module.exports.jsx = jsx4;
      module.exports.jsxs = jsxs5;
      module.exports.jsxDEV = function(t, p, k, s) {
        return (s ? jsxs5 : jsx4)(t, p, k);
      };
      module.exports.Fragment = R.Fragment;
    }
  });

  // src/index.ts
  var index_exports = {};
  __export(index_exports, {
    Badge: () => Badge,
    Button: () => Button,
    Card: () => Card,
    Input: () => Input,
    Stack: () => Stack,
    color: () => color,
    font: () => font,
    leading: () => leading,
    motion: () => motion,
    radius: () => radius,
    shadow: () => shadow,
    space: () => space,
    text: () => text,
    tokens: () => tokens,
    weight: () => weight
  });
  init_define_import_meta_env();

  // src/components/Button.tsx
  init_define_import_meta_env();
  var import_react = __toESM(require_react_shim(), 1);
  var import_jsx_runtime = __toESM(require_react_shim(), 1);
  var Button = import_react.default.forwardRef(
    function Button2({
      variant = "secondary",
      size = "md",
      fullWidth = false,
      iconLeft,
      iconRight,
      className,
      children,
      type = "button",
      ...rest
    }, ref) {
      const classes = [
        "ds-button",
        `ds-button--${variant}`,
        `ds-button--${size}`,
        fullWidth ? "ds-button--full" : null,
        className
      ].filter(Boolean).join(" ");
      return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("button", { ref, type, className: classes, ...rest, children: [
        iconLeft,
        children,
        iconRight
      ] });
    }
  );

  // src/components/Badge.tsx
  init_define_import_meta_env();
  var import_jsx_runtime2 = __toESM(require_react_shim(), 1);
  function Badge({
    tone = "neutral",
    dot = false,
    className,
    children,
    ...rest
  }) {
    const classes = ["ds-badge", `ds-badge--${tone}`, className].filter(Boolean).join(" ");
    return /* @__PURE__ */ (0, import_jsx_runtime2.jsxs)("span", { className: classes, ...rest, children: [
      dot ? /* @__PURE__ */ (0, import_jsx_runtime2.jsx)("span", { className: "ds-badge__dot", "aria-hidden": "true" }) : null,
      children
    ] });
  }

  // src/components/Card.tsx
  init_define_import_meta_env();
  var import_jsx_runtime3 = __toESM(require_react_shim(), 1);
  function Card({
    title,
    subtitle,
    footer,
    elevation = "flat",
    interactive = false,
    className,
    children,
    ...rest
  }) {
    const classes = [
      "ds-card",
      `ds-card--${elevation}`,
      interactive ? "ds-card--interactive" : null,
      className
    ].filter(Boolean).join(" ");
    const hasHeader = title != null || subtitle != null;
    return /* @__PURE__ */ (0, import_jsx_runtime3.jsxs)(
      "div",
      {
        className: classes,
        tabIndex: interactive ? 0 : void 0,
        ...rest,
        children: [
          hasHeader ? /* @__PURE__ */ (0, import_jsx_runtime3.jsxs)("div", { className: "ds-card__header", children: [
            title != null ? /* @__PURE__ */ (0, import_jsx_runtime3.jsx)("h3", { className: "ds-card__title", children: title }) : null,
            subtitle != null ? /* @__PURE__ */ (0, import_jsx_runtime3.jsx)("p", { className: "ds-card__subtitle", children: subtitle }) : null
          ] }) : null,
          /* @__PURE__ */ (0, import_jsx_runtime3.jsx)("div", { className: "ds-card__body", children }),
          footer != null ? /* @__PURE__ */ (0, import_jsx_runtime3.jsx)("div", { className: "ds-card__footer", children: footer }) : null
        ]
      }
    );
  }

  // src/components/Input.tsx
  init_define_import_meta_env();
  var import_react2 = __toESM(require_react_shim(), 1);
  var import_jsx_runtime4 = __toESM(require_react_shim(), 1);
  var idCounter = 0;
  var Input = import_react2.default.forwardRef(
    function Input2({ label, hint, error, id, className, required, ...rest }, ref) {
      const generatedId = import_react2.default.useMemo(() => `ds-input-${++idCounter}`, []);
      const inputId = id ?? generatedId;
      const messageId = `${inputId}-message`;
      const message = error ?? hint;
      const inputClasses = ["ds-input", error ? "ds-input--invalid" : null, className].filter(Boolean).join(" ");
      return /* @__PURE__ */ (0, import_jsx_runtime4.jsxs)("div", { className: "ds-field", children: [
        label ? /* @__PURE__ */ (0, import_jsx_runtime4.jsxs)("label", { className: "ds-field__label", htmlFor: inputId, children: [
          label,
          required ? /* @__PURE__ */ (0, import_jsx_runtime4.jsx)("span", { className: "ds-field__required", "aria-hidden": "true", children: "*" }) : null
        ] }) : null,
        /* @__PURE__ */ (0, import_jsx_runtime4.jsx)(
          "input",
          {
            ref,
            id: inputId,
            className: inputClasses,
            required,
            "aria-invalid": error ? true : void 0,
            "aria-describedby": message ? messageId : void 0,
            ...rest
          }
        ),
        message ? /* @__PURE__ */ (0, import_jsx_runtime4.jsx)(
          "span",
          {
            id: messageId,
            className: [
              "ds-field__message",
              error ? "ds-field__message--error" : null
            ].filter(Boolean).join(" "),
            children: message
          }
        ) : null
      ] });
    }
  );

  // src/components/Stack.tsx
  init_define_import_meta_env();
  var import_react3 = __toESM(require_react_shim(), 1);

  // tokens/tokens.ts
  init_define_import_meta_env();
  var color = {
    bg: "var(--color-bg)",
    surface: "var(--color-surface)",
    surfaceRaised: "var(--color-surface-raised)",
    border: "var(--color-border)",
    borderStrong: "var(--color-border-strong)",
    text: "var(--color-text)",
    textMuted: "var(--color-text-muted)",
    textInverse: "var(--color-text-inverse)",
    accent: "var(--color-accent)",
    accentHover: "var(--color-accent-hover)",
    accentSubtle: "var(--color-accent-subtle)",
    accentBorder: "var(--color-accent-border)",
    success: "var(--color-success)",
    successSubtle: "var(--color-success-subtle)",
    warning: "var(--color-warning)",
    warningSubtle: "var(--color-warning-subtle)",
    danger: "var(--color-danger)",
    dangerSubtle: "var(--color-danger-subtle)"
  };
  var font = {
    sans: "var(--font-sans)",
    serif: "var(--font-serif)",
    mono: "var(--font-mono)"
  };
  var text = {
    xs: "var(--text-xs)",
    sm: "var(--text-sm)",
    base: "var(--text-base)",
    lg: "var(--text-lg)",
    xl: "var(--text-xl)",
    "2xl": "var(--text-2xl)",
    "3xl": "var(--text-3xl)"
  };
  var leading = {
    tight: "var(--leading-tight)",
    normal: "var(--leading-normal)",
    relaxed: "var(--leading-relaxed)"
  };
  var weight = {
    regular: "var(--weight-regular)",
    medium: "var(--weight-medium)",
    semibold: "var(--weight-semibold)"
  };
  var space = {
    0: "var(--space-0)",
    1: "var(--space-1)",
    2: "var(--space-2)",
    3: "var(--space-3)",
    4: "var(--space-4)",
    5: "var(--space-5)",
    6: "var(--space-6)",
    7: "var(--space-7)",
    8: "var(--space-8)"
  };
  var radius = {
    sm: "var(--radius-sm)",
    md: "var(--radius-md)",
    lg: "var(--radius-lg)",
    full: "var(--radius-full)"
  };
  var shadow = {
    sm: "var(--shadow-sm)",
    md: "var(--shadow-md)",
    lg: "var(--shadow-lg)"
  };
  var motion = {
    fast: "var(--duration-fast)",
    base: "var(--duration-base)",
    ease: "var(--ease-standard)"
  };
  var tokens = {
    color,
    font,
    text,
    leading,
    weight,
    space,
    radius,
    shadow,
    motion
  };

  // src/components/Stack.tsx
  function Stack({
    direction = "column",
    gap = 4,
    align,
    justify,
    wrap = false,
    as: Tag = "div",
    style,
    children,
    ...rest
  }) {
    const layout = {
      display: "flex",
      flexDirection: direction,
      gap: space[gap],
      alignItems: align,
      justifyContent: justify,
      flexWrap: wrap ? "wrap" : "nowrap",
      ...style
    };
    return import_react3.default.createElement(Tag, { style: layout, ...rest }, children);
  }
  return __toCommonJS(index_exports);
})();
window.JosieDesignSystem=JosieDesignSystem.__dsMainNs?Object.assign({},JosieDesignSystem,JosieDesignSystem.__dsMainNs,{__dsMainNs:undefined}):JosieDesignSystem;

"""Single-file HTML/CSS/JS web UI for Meal Manager — Bootstrap 5 edition."""

HTML = r"""<!DOCTYPE html>
<html lang="en" data-bs-theme="dark">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Meal Manager</title>
<!-- Bootstrap 5 CSS (CDN) -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"/>
<!-- Bootstrap Icons -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css"/>
<style>
  /* ── colour tokens ── */
  :root {
    --mm-accent:   #6c8ef5;
    --mm-accent2:  #a78bfa;
    --mm-green:    #34d399;
    --mm-yellow:   #fbbf24;
    --mm-red:      #f87171;
    --mm-surface:  #1a1d27;
    --mm-card:     #22263a;
    --mm-border:   #2e3350;
    --mm-muted:    #8892a4;
  }

  /* ── base ── */
  body { background: #0f1117; font-family: 'Segoe UI', system-ui, sans-serif; }

  /* ── sidebar ── */
  #sidebar {
    width: 230px; min-height: 100vh;
    background: var(--mm-surface);
    border-right: 1px solid var(--mm-border);
    display: flex; flex-direction: column;
    transition: width .25s ease;
    flex-shrink: 0;
    overflow: hidden;
  }
  /* collapsed: shrink to a thin strip so the toggle button stays visible */
  #sidebar.collapsed { width: 48px; }
  #sidebar.collapsed #sidebar-brand-text,
  #sidebar.collapsed .nav-link-text,
  #sidebar.collapsed #sidebar-nav { display: none; }
  #sidebar.collapsed #sidebar-brand { justify-content: center; padding: 14px 0; border-bottom-color: var(--mm-border); }

  #sidebar-brand {
    padding: 16px 20px 14px;
    font-size: 17px; font-weight: 700;
    color: var(--mm-accent);
    cursor: pointer;
    user-select: none;
    border-bottom: 1px solid var(--mm-border);
    white-space: nowrap;
    display: flex; align-items: center; gap: 10px;
    flex-shrink: 0;
  }
  #sidebar-brand:hover { color: #fff; }
  #sidebar-toggle-icon { font-size: 20px; flex-shrink: 0; line-height: 1; }

  .nav-link {
    color: var(--mm-muted) !important;
    padding: 10px 20px;
    font-size: 14px;
    border-left: 3px solid transparent;
    white-space: nowrap;
    transition: all .15s;
    display: flex; align-items: center; gap: 10px;
  }
  .nav-link:hover { color: #e2e8f0 !important; background: var(--mm-card); }
  .nav-link.active {
    color: var(--mm-accent) !important;
    background: var(--mm-card);
    border-left-color: var(--mm-accent);
  }

  /* ── mobile top bar ── */
  #topbar {
    display: none;
    background: var(--mm-surface);
    border-bottom: 1px solid var(--mm-border);
    padding: 10px 16px;
    align-items: center; gap: 12px;
    position: sticky; top: 0; z-index: 200;
  }
  #topbar-title { font-size: 16px; font-weight: 700; color: var(--mm-accent); }
  #topbar-toggle { background: none; border: none; color: var(--mm-muted); font-size: 22px; line-height: 1; cursor: pointer; }

  /* ── mobile drawer overlay ── */
  #sidebar-overlay {
    display: none; position: fixed; inset: 0;
    background: rgba(0,0,0,.55); z-index: 300;
  }
  #sidebar-overlay.show { display: block; }

  /* ── mobile sidebar drawer ── */
  @media (max-width: 767px) {
    #topbar { display: flex; }
    #sidebar {
      position: fixed; top: 0; left: 0; height: 100%;
      z-index: 400; transform: translateX(-100%);
      width: 230px !important;
    }
    #sidebar.mobile-open { transform: translateX(0); }
    #main-content { padding: 16px !important; }
  }

  /* ── sections ── */
  .mm-section { display: none; }
  .mm-section.active { display: block; }

  /* ── cards ── */
  .mm-card {
    background: var(--mm-card);
    border: 1px solid var(--mm-border);
    border-radius: 10px;
    padding: 22px;
    margin-bottom: 20px;
  }

  /* ── form controls override ── */
  .form-control, .form-select {
    background: var(--mm-surface) !important;
    border-color: var(--mm-border) !important;
    color: #e2e8f0 !important;
  }
  .form-control:focus, .form-select:focus {
    border-color: var(--mm-accent) !important;
    box-shadow: 0 0 0 3px rgba(108,142,245,.2) !important;
  }
  .form-control::placeholder { color: var(--mm-muted); }
  .form-label { font-size: 13px; color: var(--mm-muted); font-weight: 500; margin-bottom: 5px; }
  textarea.form-control { resize: vertical; min-height: 60px; }
  #f-recipe { min-height: 120px; }

  /* ── buttons ── */
  .btn-mm-primary   { background: var(--mm-accent); color: #fff; border: none; }
  .btn-mm-primary:hover { background: #5a7de8; color: #fff; }
  .btn-mm-secondary { background: var(--mm-surface); border: 1px solid var(--mm-border); color: #e2e8f0; }
  .btn-mm-secondary:hover { border-color: var(--mm-accent); color: var(--mm-accent); }
  .btn-mm-danger    { background: transparent; border: 1px solid var(--mm-border); color: var(--mm-red); }
  .btn-mm-danger:hover { background: var(--mm-red); color: #fff; border-color: var(--mm-red); }
  .btn-icon {
    background: var(--mm-surface); border: 1px solid var(--mm-border);
    color: var(--mm-muted); cursor: pointer; font-size: 15px;
    width: 34px; height: 34px; border-radius: 6px;
    display: inline-flex; align-items: center; justify-content: center;
    transition: all .15s;
  }
  .btn-icon:hover { border-color: var(--mm-red); color: var(--mm-red); }

  /* ── badges ── */
  .badge-breakfast { background: #3d2e0a !important; color: var(--mm-yellow) !important; }
  .badge-lunch     { background: #0d2e1a !important; color: var(--mm-green)  !important; }
  .badge-dinner    { background: #0d1a3d !important; color: var(--mm-accent) !important; }
  .badge-snack     { background: #2a1a3d !important; color: #c084fc         !important; }
  .meal-type-badge { border-radius: 6px; font-size: 11px; font-weight: 700; padding: 3px 9px; text-transform: uppercase; letter-spacing: .5px; white-space: nowrap; }

  /* ── recipe meal-type filter buttons (Recipes tab) ── */
  .recipe-type-btn {
    border: 1px solid var(--mm-border); background: var(--mm-surface); color: var(--mm-muted);
    border-radius: 20px; font-size: 12px; font-weight: 700; padding: 5px 14px; cursor: pointer;
    text-transform: uppercase; letter-spacing: .5px; transition: all .15s;
  }
  .recipe-type-btn:hover { border-color: var(--mm-accent); }
  .recipe-type-btn.active[data-type="all"]       { background: var(--mm-accent); color: #0f1117; border-color: var(--mm-accent); }
  .recipe-type-btn.active[data-type="breakfast"] { background: #3d2e0a; color: var(--mm-yellow); border-color: var(--mm-yellow); }
  .recipe-type-btn.active[data-type="lunch"]     { background: #0d2e1a; color: var(--mm-green);  border-color: var(--mm-green); }
  .recipe-type-btn.active[data-type="dinner"]    { background: #0d1a3d; color: var(--mm-accent); border-color: var(--mm-accent); }
  .recipe-type-btn.active[data-type="snack"]     { background: #2a1a3d; color: #c084fc;          border-color: #c084fc; }

  /* ── autocomplete ── */
  .autocomplete-wrap { position: relative; }
  .autocomplete-list {
    position: absolute; top: 100%; left: 0; right: 0;
    background: var(--mm-card); border: 1px solid var(--mm-accent);
    border-top: none; border-radius: 0 0 8px 8px;
    z-index: 500; max-height: 220px; overflow-y: auto;
  }
  .autocomplete-item {
    padding: 9px 14px; cursor: pointer; font-size: 14px;
    display: flex; align-items: center; gap: 10px;
    border-bottom: 1px solid var(--mm-border);
  }
  .autocomplete-item:last-child { border-bottom: none; }
  .autocomplete-item:hover, .autocomplete-item.selected { background: var(--mm-surface); color: var(--mm-accent); }
  .autocomplete-item .ac-badge { font-size: 10px; font-weight: 700; padding: 2px 7px; border-radius: 4px; text-transform: uppercase; }

  /* ── product row ── */
  .product-row { display: grid; grid-template-columns: 1fr 120px 36px; gap: 8px; align-items: center; margin-bottom: 8px; }
  .product-row input { margin: 0; }

  /* ── meal log ── */
  .meal-card {
    background: var(--mm-card); border: 1px solid var(--mm-border);
    border-radius: 10px; padding: 14px 18px; margin-bottom: 8px;
    display: flex; align-items: flex-start; gap: 14px;
  }
  .meal-info { flex: 1; min-width: 0; }
  .meal-name { font-weight: 600; font-size: 15px; margin-bottom: 3px; }
  .meal-products { font-size: 13px; color: var(--mm-muted); }
  .meal-notes { font-size: 12px; color: var(--mm-accent2); margin-top: 3px; font-style: italic; }

  /* ── charts ── */
  .bar-row { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; font-size: 13px; }
  .bar-label { width: 130px; text-align: right; color: var(--mm-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; flex-shrink: 0; }
  .bar-track { flex: 1; background: var(--mm-surface); border-radius: 4px; height: 14px; overflow: hidden; }
  .bar-fill  { height: 100%; border-radius: 4px; transition: width .4s ease; }
  .bar-val   { width: 36px; color: var(--mm-muted); font-size: 12px; text-align: right; flex-shrink: 0; }
  .heatmap-row { display: flex; align-items: center; gap: 8px; margin-bottom: 5px; font-size: 12px; }
  .heatmap-date { width: 60px; color: var(--mm-muted); flex-shrink: 0; }
  .heatmap-cal { margin-left: auto; color: var(--mm-accent2); font-size: 11px; white-space: nowrap; }
  .dot { width: 22px; height: 22px; border-radius: 5px; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 700; flex-shrink: 0; }
  .dot-on  { opacity: 1; }
  .dot-off { opacity: .15; }
  .dot-b { background: #3d2e0a; color: var(--mm-yellow); }
  .dot-l { background: #0d2e1a; color: var(--mm-green); }
  .dot-d { background: #0d1a3d; color: var(--mm-accent); }

  /* ── recommendation ── */
  .rec-card {
    background: var(--mm-card); border: 1px solid var(--mm-border);
    border-radius: 10px; padding: 18px;
  }
  .rec-type  { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px; }
  .rec-name  { font-size: 17px; font-weight: 700; margin-bottom: 8px; }
  .rec-score { font-size: 12px; color: var(--mm-muted); margin-bottom: 6px; }
  .score-bar { background: var(--mm-surface); border-radius: 4px; height: 6px; margin-bottom: 10px; overflow: hidden; }
  .score-fill { height: 100%; border-radius: 4px; background: linear-gradient(90deg, var(--mm-accent), var(--mm-green)); }
  .rec-reason { font-size: 12px; color: var(--mm-muted); font-style: italic; margin-bottom: 10px; }
  .rec-products { display: flex; flex-wrap: wrap; gap: 5px; }
  .tag { background: var(--mm-surface); border: 1px solid var(--mm-border); border-radius: 20px; font-size: 11px; padding: 3px 10px; color: var(--mm-muted); }

  /* ── week view ── */
  .week-day-row { background: var(--mm-card); border: 1px solid var(--mm-border); border-radius: 10px; overflow: hidden; margin-bottom: 10px; }
  .week-day-header { display: flex; align-items: center; gap: 12px; padding: 12px 16px; background: var(--mm-surface); cursor: pointer; user-select: none; flex-wrap: wrap; gap: 8px; }
  .week-day-name { font-weight: 700; font-size: 15px; min-width: 90px; }
  .week-day-date { font-size: 12px; color: var(--mm-muted); }
  .week-day-pills { display: flex; gap: 6px; flex: 1; flex-wrap: wrap; }
  .week-pill { font-size: 11px; padding: 3px 10px; border-radius: 20px; font-weight: 600; }
  .pill-b { background:#3d2e0a; color:var(--mm-yellow); }
  .pill-l { background:#0d2e1a; color:var(--mm-green);  }
  .pill-d { background:#0d1a3d; color:var(--mm-accent); }
  .week-day-arrow { color: var(--mm-muted); font-size: 16px; transition: transform .2s; }
  .week-day-row.open .week-day-arrow { transform: rotate(90deg); }
  .week-day-body { display: none; padding: 14px 16px; }
  .week-day-row.open .week-day-body { display: block; }

  /* ── recipes ── */
  .recipe-card { background: var(--mm-card); border: 1px solid var(--mm-border); border-radius: 10px; overflow: hidden; margin-bottom: 14px; transition: border-color .15s; }
  .recipe-card:hover { border-color: var(--mm-accent); }
  .recipe-card-header { padding: 14px 18px; display: flex; align-items: center; gap: 10px; cursor: pointer; flex-wrap: wrap; }
  .recipe-card-title { flex: 1; font-weight: 600; font-size: 15px; }
  .recipe-card-arrow { color: var(--mm-muted); font-size: 18px; transition: transform .2s; flex-shrink: 0; }
  .recipe-card.open .recipe-card-arrow { transform: rotate(90deg); }
  .recipe-card-labels { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
  /* Hide the meal-type/source/calorie labels on each recipe card on small screens only —
     purely visual, the underlying data is untouched and still shown when a card is expanded. */
  @media (max-width: 767px) {
    .recipe-card-labels { display: none; }
  }
  .recipe-card-body { display: none; padding: 0 18px 18px; border-top: 1px solid var(--mm-border); }
  .recipe-card.open .recipe-card-body { display: block; }
  .recipe-section-title { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: var(--mm-muted); margin: 14px 0 8px; }
  .ingredient-list { display: flex; flex-direction: column; gap: 4px; }
  .ingredient-row { display: flex; justify-content: space-between; font-size: 13px; padding: 5px 0; border-bottom: 1px solid var(--mm-border); }
  .ingredient-row:last-child { border-bottom: none; }
  .ingredient-qty { color: var(--mm-accent2); font-size: 12px; }
  .recipe-text { font-size: 13px; line-height: 1.7; color: #e2e8f0; white-space: pre-wrap; background: var(--mm-surface); border-radius: 6px; padding: 12px 14px; margin-top: 4px; }
  .no-recipe { font-size: 13px; color: var(--mm-muted); font-style: italic; }
  .recipe-card-actions { display: flex; gap: 8px; margin-top: 14px; padding-top: 12px; border-top: 1px solid var(--mm-border); flex-wrap: wrap; }
  .edit-panel { display: none; margin-top: 14px; padding-top: 14px; border-top: 1px solid var(--mm-border); }
  .edit-panel.visible { display: block; }
  .edit-panel label { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: var(--mm-muted); display: block; margin-bottom: 6px; }
  .edit-panel textarea { width: 100%; min-height: 120px; resize: vertical; font-size: 13px; line-height: 1.7; }
  .edit-ingredient-row { display: grid; grid-template-columns: 1fr 110px 34px; gap: 6px; align-items: center; margin-bottom: 6px; }
  .edit-ingredient-row input { font-size: 13px; }

  /* ── meal type multi-select dropdown ── */
  .ms-dropdown-wrap { position: relative; }
  .ms-dropdown-menu {
    position: absolute; top: calc(100% + 4px); left: 0; right: 0; z-index: 20;
    background: var(--mm-card); border: 1px solid var(--mm-border); border-radius: 8px;
    padding: 6px; box-shadow: 0 8px 24px rgba(0,0,0,.4);
  }
  .ms-dropdown-item { display: flex; align-items: center; gap: 8px; padding: 7px 8px; border-radius: 6px; font-size: 13px; cursor: pointer; margin: 0; }
  .ms-dropdown-item:hover { background: var(--mm-surface); }
  .ms-dropdown-item input { accent-color: var(--mm-accent); cursor: pointer; }

  /* ── modal overlay (meal detail, fridge → shopping list, ...) ── */
  .modal-overlay {
    position: fixed; inset: 0; background: rgba(0,0,0,.6);
    display: none; align-items: center; justify-content: center; z-index: 9500; padding: 20px;
  }
  .modal-overlay.show { display: flex; }
  .meal-detail-card {
    background: var(--mm-card); border: 1px solid var(--mm-border); border-radius: 12px;
    padding: 22px; width: 100%; max-width: 520px; max-height: 85vh; overflow-y: auto;
    box-shadow: 0 8px 40px rgba(0,0,0,.5); position: relative;
  }
  .meal-detail-close {
    position: absolute; top: 14px; right: 14px; background: none; border: none;
    color: var(--mm-muted); font-size: 18px; cursor: pointer; padding: 4px;
  }
  .meal-detail-close:hover { color: #fff; }
  .meal-detail-title { font-size: 18px; font-weight: 700; margin-bottom: 4px; padding-right: 24px; }
  .wm-slot-name-clickable { cursor: pointer; text-decoration: underline dotted; text-decoration-color: var(--mm-muted); }
  .wm-slot-name-clickable:hover { color: var(--mm-accent); }

  /* ── cooking method checkboxes ── */
  .method-check-label { display: inline-flex; align-items: center; gap: 6px; font-size: 13px; cursor: pointer; margin: 0 16px 0 0; }
  .method-check-label input { accent-color: var(--mm-accent); cursor: pointer; }

  /* ── shopping list ── */
  .shop-item { display: flex; align-items: center; gap: 10px; padding: 10px 14px; background: var(--mm-card); border: 1px solid var(--mm-border); border-radius: 10px; margin-bottom: 8px; transition: opacity .2s; }
  .shop-item.done { opacity: .45; }
  .shop-item.done .shop-name { text-decoration: line-through; color: var(--mm-muted); }
  .shop-check { width: 18px; height: 18px; cursor: pointer; accent-color: var(--mm-green); flex-shrink: 0; }
  .shop-name  { flex: 1; font-size: 14px; }
  .shop-qty   { font-size: 12px; color: var(--mm-muted); min-width: 60px; }
  .shop-del   { background: none; border: none; color: var(--mm-muted); cursor: pointer; font-size: 16px; padding: 0 4px; }
  .shop-del:hover { color: var(--mm-red); }

  /* ── fridge ── */
  .fridge-warn { color: var(--mm-yellow); font-weight: 700; margin-right: 6px; }

  /* ── toast ── */
  #toast { position: fixed; bottom: 24px; right: 24px; background: var(--mm-green); color: #0f1117; padding: 12px 20px; border-radius: 8px; font-weight: 600; font-size: 14px; opacity: 0; transform: translateY(10px); transition: all .25s; pointer-events: none; z-index: 9999; max-width: calc(100vw - 48px); }
  #toast.error { background: var(--mm-red); color: #fff; }
  #toast.show  { opacity: 1; transform: translateY(0); }

  /* ── weekly menu ── */
  .wm-day-card { background: var(--mm-card); border: 1px solid var(--mm-border); border-radius: 10px; margin-bottom: 14px; overflow: hidden; }
  .wm-day-header { display: flex; align-items: center; justify-content: space-between; padding: 12px 18px; background: var(--mm-surface); border-bottom: 1px solid var(--mm-border); flex-wrap: wrap; gap: 8px; }
  .wm-day-name  { font-weight: 700; font-size: 15px; }
  .wm-day-date  { font-size: 12px; color: var(--mm-muted); }
  .wm-slots     { padding: 12px 18px; display: flex; flex-direction: column; gap: 10px; }
  .wm-slot-row  { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
  .wm-slot-label{ font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: .5px; width: 70px; flex-shrink: 0; }
  .wm-slot-name { flex: 1; min-width: 120px; font-size: 14px; color: #e2e8f0; }
  .wm-slot-name.empty-slot { color: var(--mm-muted); font-style: italic; }
  .wm-slot-products { display: flex; flex-wrap: wrap; gap: 4px; }
  .wm-edit-row  { display: none; align-items: center; gap: 8px; flex-wrap: wrap; width: 100%; margin-top: 4px; }
  .wm-edit-row.visible { display: flex; }

  /* ── misc ── */
  .empty { color: var(--mm-muted); font-style: italic; padding: 16px 0; }
  .date-label { font-size: 12px; font-weight: 700; color: var(--mm-muted); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; }

  /* ── auth overlay ── */
  #auth-overlay {
    position: fixed; inset: 0; background: #0f1117;
    display: flex; align-items: center; justify-content: center;
    z-index: 9000;
  }
  #auth-overlay.hidden { display: none; }
  .auth-card {
    background: var(--mm-card); border: 1px solid var(--mm-border);
    border-radius: 14px; padding: 36px 32px; width: 100%;
    max-width: 420px; box-shadow: 0 8px 40px rgba(0,0,0,.5);
  }
  .auth-title { font-size: 22px; font-weight: 700; color: var(--mm-accent); margin-bottom: 6px; }
  .auth-subtitle { font-size: 13px; color: var(--mm-muted); margin-bottom: 24px; }
  .auth-tabs { display: flex; gap: 0; margin-bottom: 24px; border-bottom: 1px solid var(--mm-border); }
  .auth-tab { flex: 1; text-align: center; padding: 10px; font-size: 14px; font-weight: 600;
    color: var(--mm-muted); cursor: pointer; border-bottom: 2px solid transparent; transition: all .15s; }
  .auth-tab.active { color: var(--mm-accent); border-bottom-color: var(--mm-accent); }
  .auth-form { display: none; }
  .auth-form.active { display: block; }
  .auth-link { font-size: 13px; color: var(--mm-accent); cursor: pointer; text-decoration: underline; }
  .auth-link:hover { color: #fff; }
  #auth-error { display: none; }

  /* ── user bar ── */
  #user-bar {
    background: var(--mm-surface); border-bottom: 1px solid var(--mm-border);
    padding: 6px 20px; display: flex; align-items: center; gap: 10px;
    font-size: 13px; color: var(--mm-muted); flex-shrink: 0;
  }
  #user-bar .user-name { color: var(--mm-accent); font-weight: 600; }

  /* ── family tab ── */
  .family-member-row { display: flex; align-items: center; gap: 10px; padding: 10px 14px;
    background: var(--mm-card); border: 1px solid var(--mm-border); border-radius: 10px; margin-bottom: 8px; }
  .family-member-info { flex: 1; }
  .family-member-name { font-weight: 600; font-size: 14px; }
  .family-member-email { font-size: 12px; color: var(--mm-muted); }
  .family-status-badge { font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 20px; text-transform: uppercase; }
  .status-active  { background: #0d2e1a; color: var(--mm-green); }
  .status-pending { background: #3d2e0a; color: var(--mm-yellow); }
</style>
</head>
<body>

<!-- ── auth overlay ── -->
<div id="auth-overlay">
  <div class="auth-card">
    <div class="auth-title">🍽 Meal Manager</div>
    <div class="auth-subtitle">Track your meals, plan your week.</div>
    <div class="auth-tabs">
      <div class="auth-tab active" id="tab-login"    onclick="authTab('login')">Log in</div>
      <div class="auth-tab"        id="tab-register" onclick="authTab('register')">Register</div>
    </div>
    <div id="auth-error" class="alert alert-danger py-2 mb-3" style="font-size:13px"></div>

    <!-- Login form -->
    <div class="auth-form active" id="form-login">
      <div class="mb-3">
        <label class="form-label">Username or email</label>
        <input id="login-user" class="form-control" type="text" placeholder="you@example.com" autocomplete="username"/>
      </div>
      <div class="mb-3">
        <label class="form-label">Password</label>
        <input id="login-pass" class="form-control" type="password" autocomplete="current-password"
               onkeydown="if(event.key==='Enter')doLogin()"/>
      </div>
      <button class="btn btn-mm-primary w-100 mb-3" onclick="doLogin()">Log in</button>
      <div class="text-center">
        <span class="auth-link" onclick="authTab('forgot')">Forgot password?</span>
      </div>
    </div>

    <!-- Register form -->
    <div class="auth-form" id="form-register">
      <div class="mb-3">
        <label class="form-label">Username</label>
        <input id="reg-user" class="form-control" type="text" autocomplete="username"/>
      </div>
      <div class="mb-3">
        <label class="form-label">Email</label>
        <input id="reg-email" class="form-control" type="email" autocomplete="email"/>
      </div>
      <div class="mb-3">
        <label class="form-label">Password <small class="text-muted">(min 6 characters)</small></label>
        <input id="reg-pass" class="form-control" type="password" autocomplete="new-password"
               onkeydown="if(event.key==='Enter')doRegister()"/>
      </div>
      <button class="btn btn-mm-primary w-100" onclick="doRegister()">Create account</button>
    </div>

    <!-- Forgot password form -->
    <div class="auth-form" id="form-forgot">
      <p style="font-size:13px;color:var(--mm-muted)">Enter your email address and we'll send you a link to reset your password.</p>
      <div class="mb-3">
        <label class="form-label">Email</label>
        <input id="forgot-email" class="form-control" type="email"
               onkeydown="if(event.key==='Enter')doForgot()"/>
      </div>
      <button class="btn btn-mm-primary w-100 mb-3" onclick="doForgot()">Send reset link</button>
      <div class="text-center">
        <span class="auth-link" onclick="authTab('login')">← Back to login</span>
      </div>
    </div>
  </div>
</div>

<!-- ── mobile top bar ── -->
<div id="topbar">
  <button id="topbar-toggle" onclick="toggleSidebar()" aria-label="Menu">
    <i class="bi bi-list"></i>
  </button>
  <span id="topbar-title">🍽 Meal Manager</span>
</div>

<!-- ── sidebar overlay (mobile) ── -->
<div id="sidebar-overlay" onclick="closeSidebar()"></div>

<!-- ── app shell ── -->
<div class="d-flex" style="min-height:100vh">

  <!-- SIDEBAR -->
  <div id="sidebar">
    <div id="sidebar-brand" onclick="toggleSidebar()" title="Toggle menu">
      <i class="bi bi-list" id="sidebar-toggle-icon"></i>
      <span id="sidebar-brand-text">🍽 Meal Manager</span>
    </div>
    <nav class="nav flex-column pt-2" id="sidebar-nav">
      <a class="nav-link active" href="#" id="nav-viz"      onclick="showSection('viz');return false">
        <i class="bi bi-bar-chart-line"></i><span class="nav-link-text">Statistics</span></a>
      <a class="nav-link" href="#" id="nav-rec"      onclick="showSection('rec');return false">
        <i class="bi bi-robot"></i><span class="nav-link-text">Recommend</span></a>
      <a class="nav-link" href="#" id="nav-fridge"   onclick="showSection('fridge');return false">
        <i class="bi bi-snow"></i><span class="nav-link-text">Fridge</span></a>
      <a class="nav-link" href="#" id="nav-shopping" onclick="showSection('shopping');return false">
        <i class="bi bi-cart3"></i><span class="nav-link-text">Shopping List</span></a>
      <a class="nav-link" href="#" id="nav-weeklymenu" onclick="showSection('weeklymenu');return false">
        <i class="bi bi-calendar2-week"></i><span class="nav-link-text">Weekly Menu</span></a>
      <a class="nav-link" href="#" id="nav-snacks"   onclick="showSection('snacks');return false">
        <i class="bi bi-apple"></i><span class="nav-link-text">Snacks</span></a>
      <a class="nav-link" href="#" id="nav-recipes"  onclick="showSection('recipes');return false">
        <i class="bi bi-book"></i><span class="nav-link-text">Recipes</span></a>
      <a class="nav-link" href="#" id="nav-add"      onclick="showSection('add');return false">
        <i class="bi bi-plus-circle"></i><span class="nav-link-text">Add Meal</span></a>
      <a class="nav-link" href="#" id="nav-log"      onclick="showSection('log');return false">
        <i class="bi bi-journal-text"></i><span class="nav-link-text">Meal Log</span></a>
      <a class="nav-link" href="#" id="nav-family"     onclick="showSection('family');return false">
        <i class="bi bi-people"></i><span class="nav-link-text">Family</span></a>
    </nav>
    <!-- user bar at bottom of sidebar -->
    <div id="user-bar" style="margin-top:auto">
      <i class="bi bi-person-circle"></i>
      <span class="user-name" id="user-bar-name">—</span>
      <button class="btn btn-sm btn-mm-secondary ms-auto" onclick="doLogout()" title="Log out">
        <i class="bi bi-box-arrow-right"></i><span class="nav-link-text ms-1">Logout</span>
      </button>
    </div>
  </div>

  <!-- MAIN CONTENT -->
  <div id="main-content" class="flex-grow-1 p-4" style="min-width:0;overflow-y:auto">

    <!-- ── ADD MEAL ── -->
    <div class="mm-section" id="section-add">
      <h2 class="mb-4">Add a Meal</h2>
      <div class="mm-card">
        <div class="row g-3">
          <div class="col-12 col-md-6">
            <label class="form-label">Meal name <span style="color:var(--mm-muted);font-weight:400">(type to search)</span></label>
            <div class="autocomplete-wrap">
              <input id="f-name" class="form-control" type="text" placeholder="e.g. Scrambled eggs"
                     autocomplete="off" oninput="acInput(this.value)" onkeydown="acKeydown(event)" onfocus="acInput(this.value)"/>
              <div id="ac-list" class="autocomplete-list" style="display:none"></div>
            </div>
          </div>
          <div class="col-6 col-md-3">
            <label class="form-label">Date</label>
            <input id="f-date" class="form-control" type="date"/>
          </div>
          <div class="col-6 col-md-3">
            <label class="form-label">Meal type</label>
            <select id="f-type" class="form-select">
              <option value="breakfast">🌅 Breakfast</option>
              <option value="lunch">☀️ Lunch</option>
              <option value="dinner">🌙 Dinner</option>
              <option value="snack">🍎 Snack</option>
            </select>
          </div>
          <div class="col-6 col-md-3">
            <label class="form-label">Calories <span style="color:var(--mm-muted);font-weight:400">(optional)</span></label>
            <input id="f-calories" class="form-control" type="number" min="0" step="1" placeholder="e.g. 450"/>
          </div>
          <div class="col-12">
            <label class="form-label">Notes (optional)</label>
            <input id="f-notes" class="form-control" type="text" placeholder="e.g. Add chili flakes"/>
          </div>
        </div>

        <div class="mt-4">
          <h6 class="text-info mb-3">Ingredients / Products</h6>
          <div id="product-list"></div>
          <button class="btn btn-sm btn-mm-secondary" onclick="addProductRow()">
            <i class="bi bi-plus"></i> Add ingredient</button>
        </div>

        <div class="mt-4">
          <h6 class="text-info mb-2">Recipe
            <small class="text-muted fw-normal">(optional — steps, tips, cooking time…)</small>
          </h6>
          <textarea id="f-recipe" class="form-control"
            placeholder="1. Boil water and cook pasta for 10 min.&#10;2. Fry cherry tomatoes in olive oil for 3 min.&#10;3. Mix together, add parmesan and serve."
            oninput="autoGrow(this)"></textarea>
        </div>

        <div class="d-flex gap-2 mt-4 flex-wrap">
          <button class="btn btn-mm-primary" onclick="submitMeal()">
            <i class="bi bi-floppy me-1"></i>Save Meal</button>
          <button class="btn btn-mm-secondary" onclick="resetForm()">Clear</button>
        </div>
      </div>
    </div>

    <!-- ── MEAL LOG ── -->
    <div class="mm-section" id="section-log">
      <h2 class="mb-4">Meal Log</h2>
      <div class="d-flex gap-2 mb-4 flex-wrap align-items-center">
        <input id="filter-date" class="form-control" type="date" style="max-width:180px" onchange="loadLog()"/>
        <button class="btn btn-sm btn-mm-secondary" onclick="document.getElementById('filter-date').value=''; loadLog()">Show all</button>
      </div>
      <div id="log-content"><p class="empty">Loading…</p></div>
    </div>

    <!-- ── SNACKS ── -->
    <div class="mm-section" id="section-snacks">
      <h2 class="mb-4">Snacks</h2>
      <div class="d-flex gap-2 mb-4 flex-wrap align-items-center">
        <div class="autocomplete-wrap" style="flex:1;min-width:180px;max-width:300px">
          <input id="snack-search" class="form-control" type="text" placeholder="Search snack recipes…"
                 autocomplete="off" oninput="snackSearchInput(this.value)"
                 onkeydown="snackSearchKeydown(event)" onfocus="snackSearchInput(this.value)"/>
          <div id="snack-ac-list" class="autocomplete-list" style="display:none"></div>
        </div>
        <label class="method-check-label">
          <input type="checkbox" id="snack-show-logged" onchange="onSnackShowLoggedChange()"/>
          Also show logged snacks
        </label>
        <input id="snack-filter-date" class="form-control" type="date" style="max-width:180px;display:none" onchange="loadSnacks()"/>
        <button class="btn btn-sm btn-mm-secondary" onclick="clearSnackFilters()">Show all</button>
      </div>
      <div id="snack-content"><p class="empty">Loading…</p></div>
    </div>

    <!-- ── RECIPES ── -->
    <div class="mm-section" id="section-recipes">
      <div class="d-flex align-items-center justify-content-between mb-4 flex-wrap gap-2">
        <h2 class="mb-0">Recipes</h2>
        <button class="btn btn-mm-primary" onclick="toggleAddRecipePanel()">
          <i class="bi bi-plus-circle me-1"></i>Add Recipe</button>
      </div>

      <!-- Add Recipe panel -->
      <div class="mm-card" id="add-recipe-panel" style="display:none;margin-bottom:24px">
        <h6 class="text-info mb-3">New Recipe</h6>
        <div class="row g-3">
          <div class="col-12 col-md-6">
            <label class="form-label">Recipe / Meal name</label>
            <input id="tr-name" class="form-control" type="text" placeholder="e.g. Mushroom risotto"/>
          </div>
          <div class="col-12 col-md-6">
            <label class="form-label">Meal type <span style="color:var(--mm-muted);font-weight:400">(pick one or more)</span></label>
            <div id="tr-type-container"></div>
          </div>
          <div class="col-6 col-md-3">
            <label class="form-label">Calories <span style="color:var(--mm-muted);font-weight:400">(optional)</span></label>
            <input id="tr-calories" class="form-control" type="number" min="0" step="1" placeholder="e.g. 450"/>
          </div>
          <div class="col-12">
            <label class="form-label">Notes (optional)</label>
            <input id="tr-notes" class="form-control" type="text" placeholder="e.g. Great for meal prep"/>
          </div>
        </div>
        <div class="mt-3">
          <h6 class="text-info mb-2">Ingredients</h6>
          <div id="tr-product-list"></div>
          <button class="btn btn-sm btn-mm-secondary" onclick="addTrProductRow()">
            <i class="bi bi-plus"></i> Add ingredient</button>
        </div>
        <div class="mt-3">
          <h6 class="text-info mb-2">Recipe steps</h6>
          <textarea id="tr-recipe" class="form-control"
            placeholder="1. Fry onions in butter for 3 min.&#10;2. Add arborio rice, stir for 2 min.&#10;3. Add wine, then ladle stock gradually…"
            oninput="autoGrow(this)"></textarea>
        </div>
        <div class="mt-3">
          <h6 class="text-info mb-2">Cooking method <small class="text-muted fw-normal">(optional)</small></h6>
          <div id="tr-method-container"></div>
        </div>
        <div class="d-flex gap-2 mt-3 flex-wrap">
          <button class="btn btn-mm-primary" onclick="submitTemplate()">
            <i class="bi bi-floppy me-1"></i>Save Recipe</button>
          <button class="btn btn-mm-secondary" onclick="toggleAddRecipePanel()">Cancel</button>
        </div>
      </div>

      <div class="mb-3 d-flex gap-2 flex-wrap">
        <input class="form-control" type="text" id="recipe-search"
               placeholder="Search recipes by name…" oninput="filterRecipes()"
               style="max-width:400px"/>
        <div class="ms-dropdown-wrap" style="max-width:200px;min-width:160px">
          <button type="button" class="form-select text-start" id="recipe-method-filter-toggle"
                  onclick="event.stopPropagation();toggleMealTypeDropdown('recipe-method-filter')">
            <span id="recipe-method-filter-label">All</span>
          </button>
          <div class="ms-dropdown-menu" id="recipe-method-filter-menu" style="display:none">
            <label class="ms-dropdown-item">
              <input type="checkbox" id="rmf-all" checked onchange="onRecipeMethodFilterChange('all')"/> All</label>
            <label class="ms-dropdown-item">
              <input type="checkbox" id="rmf-instant_pot" onchange="onRecipeMethodFilterChange('instant_pot')"/> ⏱️ Instant Pot</label>
            <label class="ms-dropdown-item">
              <input type="checkbox" id="rmf-air_fryer" onchange="onRecipeMethodFilterChange('air_fryer')"/> 🔥 Air Fryer</label>
          </div>
        </div>
      </div>
      <div class="mb-3 d-flex gap-2 flex-wrap" id="recipe-type-filter">
        <button class="recipe-type-btn active" data-type="all"       onclick="setRecipeTypeFilter('all')">All</button>
        <button class="recipe-type-btn"        data-type="breakfast" onclick="setRecipeTypeFilter('breakfast')">Breakfast</button>
        <button class="recipe-type-btn"        data-type="lunch"     onclick="setRecipeTypeFilter('lunch')">Lunch</button>
        <button class="recipe-type-btn"        data-type="dinner"    onclick="setRecipeTypeFilter('dinner')">Dinner</button>
        <button class="recipe-type-btn"        data-type="snack"     onclick="setRecipeTypeFilter('snack')">Snack</button>
      </div>
      <div id="recipes-content"><p class="empty">Loading…</p></div>
    </div>

    <!-- ── VISUALISE (Statistics) ── -->
    <div class="mm-section active" id="section-viz">
      <div class="d-flex align-items-center gap-3 mb-4 flex-wrap">
        <h2 class="mb-0">Statistics</h2>
        <select id="viz-range" class="form-select" style="max-width:170px" onchange="onVizRangeChange()">
          <option value="14">Last 14 days</option>
          <option value="30">Last 1 month</option>
          <option value="90">Last 3 months</option>
          <option value="180">Last 6 months</option>
          <option value="365">Last 12 months</option>
          <option value="all">All time</option>
          <option value="custom">Custom range…</option>
        </select>
        <input id="viz-custom-start" class="form-control" type="date" style="max-width:150px;display:none"/>
        <span id="viz-custom-sep" style="display:none;color:var(--mm-muted)">→</span>
        <input id="viz-custom-end" class="form-control" type="date" style="max-width:150px;display:none"/>
        <button class="btn btn-sm btn-mm-primary" id="viz-custom-apply" style="display:none" onclick="loadViz()">Apply</button>
        <button class="btn btn-sm btn-mm-secondary" onclick="loadViz()">
          <i class="bi bi-arrow-clockwise me-1"></i>Refresh</button>
      </div>
      <div id="viz-content" class="row g-3"></div>
    </div>

    <!-- ── RECOMMEND ── -->
    <div class="mm-section" id="section-rec">
      <h2 class="mb-4">AI Recommendation</h2>
      <div class="d-flex gap-2 mb-3 flex-wrap">
        <button class="btn btn-sm btn-mm-primary"   id="rec-mode-day"    onclick="setRecMode('day')">
          <i class="bi bi-calendar-day me-1"></i>Single day</button>
        <button class="btn btn-sm btn-mm-secondary" id="rec-mode-week"   onclick="setRecMode('week')">
          <i class="bi bi-calendar-week me-1"></i>Full week</button>
        <button class="btn btn-sm btn-mm-secondary" id="rec-mode-config" onclick="setRecMode('config')">
          <i class="bi bi-gear me-1"></i>Configuration</button>
      </div>
      <div class="mm-card mb-3" id="rec-config-panel" style="padding:14px 18px;display:none">
        <label class="form-label mb-1">Exclude ingredients from scoring <span style="color:var(--mm-muted);font-weight:400">(optional, saved)</span></label>
        <div id="rec-exclude-tags" class="d-flex flex-wrap gap-1 mb-2"></div>
        <div class="d-flex gap-2">
          <input id="rec-exclude-input" class="form-control" type="text" placeholder="e.g. rice"
                 onkeydown="if(event.key==='Enter'){event.preventDefault();addRecExclude();}"/>
          <button class="btn btn-sm btn-mm-secondary" onclick="addRecExclude()">Add</button>
        </div>
        <p class="mb-0 mt-2" style="font-size:12px;color:var(--mm-muted)">
          Saved to your account — applied to every recommendation from now on, on top of
          seasoning-scale amounts (a pinch, a teaspoon, ...) that are already ignored automatically.</p>
      </div>
      <div id="rec-day-week-panel">
        <div class="d-flex gap-2 mb-4 flex-wrap align-items-center">
          <label class="form-label mb-0 text-muted" id="rec-date-label">Target date:</label>
          <input id="rec-date" class="form-control" type="date" style="max-width:180px"/>
          <button class="btn btn-mm-primary" onclick="loadRec()">
            <i class="bi bi-stars me-1"></i>Get Recommendation</button>
          <button class="btn btn-mm-secondary" id="rec-export-btn" onclick="exportToShoppingList()" style="display:none">
            <i class="bi bi-cart-plus me-1"></i>Add to Shopping List</button>
          <button class="btn btn-mm-secondary" id="rec-to-wm-btn" onclick="sendRecToWeeklyMenu()" style="display:none">
            <i class="bi bi-calendar2-week me-1"></i>Send to Weekly Menu</button>
        </div>
        <div id="rec-content"><p class="empty">Click "Get Recommendation" to see suggested meals.</p></div>
      </div>
    </div>

    <!-- ── FRIDGE ── -->
    <div class="mm-section" id="section-fridge">
      <h2 class="mb-4">Fridge</h2>
      <div class="mm-card mb-3">
        <label class="form-label mb-1">Add items <span style="color:var(--mm-muted);font-weight:400">(one per line, e.g. "Яйце - 10 бр")</span></label>
        <textarea id="fridge-bulk-input" class="form-control" rows="3"
          placeholder="Яйце - 10 бр&#10;Черен пипер - 1000 щипки"></textarea>
        <button class="btn btn-mm-primary btn-sm mt-2" onclick="addFridgeBulk()">
          <i class="bi bi-plus-circle me-1"></i>Add to Fridge</button>
        <p class="mb-0 mt-2" style="font-size:12px;color:var(--mm-muted)">
          Also fills up automatically whenever you check items off the Shopping List and hit
          "Clear done". When exporting ingredients to the Shopping List (from a recipe, the Weekly
          Menu, or a recommendation), anything already in the Fridge is used up from here instead of
          being added to the list again.</p>
      </div>
      <div id="fridge-content"><p class="empty">Loading…</p></div>
    </div>

    <!-- ── SHOPPING LIST ── -->
    <div class="mm-section" id="section-shopping">
      <h2 class="mb-4">Shopping List</h2>
      <div class="d-flex gap-2 mb-4 flex-wrap align-items-center">
        <input id="shop-item" class="form-control" type="text" placeholder="Item name…"
               style="max-width:220px" oninput="suggestIngredientUnit(this, document.getElementById('shop-qty'))"
               onkeydown="if(event.key==='Enter')addShopItem()"/>
        <input id="shop-qty" class="form-control" type="text" placeholder="Qty (optional)"
               style="max-width:140px" onblur="checkIngredientUnit(document.getElementById('shop-item'), this)"
               onkeydown="if(event.key==='Enter')addShopItem()"/>
        <button class="btn btn-mm-primary btn-sm" onclick="addShopItem()">
          <i class="bi bi-plus"></i> Add item</button>
        <button class="btn btn-mm-secondary btn-sm ms-auto" onclick="clearDoneItems()">
          <i class="bi bi-trash me-1"></i>Clear done</button>
      </div>
      <div id="shop-content"><p class="empty">Your shopping list is empty.</p></div>
    </div>

    <!-- ── WEEKLY MENU ── -->
    <div class="mm-section" id="section-weeklymenu">
      <div class="d-flex align-items-center justify-content-between mb-4 flex-wrap gap-2">
        <h2 class="mb-0">Weekly Menu</h2>
        <div class="d-flex gap-2 flex-wrap align-items-center">
          <button class="btn btn-sm btn-mm-secondary" onclick="wmPrevWeek()">
            <i class="bi bi-chevron-left"></i></button>
          <span id="wm-week-label" class="text-muted small fw-semibold px-1"></span>
          <button class="btn btn-sm btn-mm-secondary" onclick="wmNextWeek()">
            <i class="bi bi-chevron-right"></i></button>
          <button class="btn btn-sm btn-mm-danger"   onclick="wmClearWeek()">
            <i class="bi bi-trash me-1"></i>Clear week</button>
        </div>
      </div>
      <div id="wm-content"><p class="empty">Loading…</p></div>
    </div>

    <!-- ── FAMILY ── -->
    <div class="mm-section" id="section-family">
      <h2 class="mb-4">Family Sharing</h2>
      <div class="mm-card mb-4">
        <p style="font-size:14px;color:var(--mm-muted)">
          Share all your meals, recipes, shopping list and weekly menu with family members.
          When someone joins your family group, they see and edit the same data as you.
        </p>
        <div id="family-content"><p class="empty">Loading…</p></div>
      </div>

      <!-- Create group -->
      <div class="mm-card" id="family-create-panel" style="display:none">
        <h5 class="mb-3">Create a family group</h5>
        <div class="d-flex gap-2 flex-wrap">
          <input id="family-group-name" class="form-control" style="max-width:260px"
                 type="text" value="Family" placeholder="Group name"/>
          <button class="btn btn-mm-primary" onclick="familyCreate()">
            <i class="bi bi-plus-circle me-1"></i>Create group</button>
        </div>
      </div>

      <!-- Invite member -->
      <div class="mm-card" id="family-invite-panel" style="display:none">
        <h5 class="mb-3">Invite a member by email</h5>
        <div class="d-flex gap-2 flex-wrap">
          <input id="family-invite-email" class="form-control" style="max-width:300px"
                 type="email" placeholder="friend@example.com"/>
          <button class="btn btn-mm-primary" onclick="familyInvite()">
            <i class="bi bi-envelope me-1"></i>Send invite</button>
        </div>
        <p class="mt-2" style="font-size:12px;color:var(--mm-muted)">
          The invited user must log in and click "Accept invite" in their own Family tab.
        </p>
      </div>

      <!-- Accept invite -->
      <div class="mm-card" id="family-accept-panel" style="display:none">
        <h5 class="mb-3">Pending invite</h5>
        <p style="font-size:14px;color:var(--mm-muted)">You have a pending family invite.</p>
        <button class="btn btn-mm-primary" onclick="familyAccept()">
          <i class="bi bi-check-circle me-1"></i>Accept invite</button>
      </div>
    </div>

  </div><!-- /main-content -->
</div><!-- /app shell -->

<!-- ── meal detail modal (Weekly Menu → click a meal name) ── -->
<div id="meal-detail-overlay" class="modal-overlay" onclick="closeMealDetail()">
  <div class="meal-detail-card" onclick="event.stopPropagation()">
    <button class="meal-detail-close" onclick="closeMealDetail()" title="Close">✕</button>
    <div id="meal-detail-body"></div>
  </div>
</div>

<!-- ── fridge → shopping list modal ── -->
<div id="fridge-send-overlay" class="modal-overlay" onclick="closeFridgeSendModal()">
  <div class="meal-detail-card" style="max-width:360px" onclick="event.stopPropagation()">
    <button class="meal-detail-close" onclick="closeFridgeSendModal()" title="Close">✕</button>
    <div class="meal-detail-title" id="fridge-send-title">Add to Shopping List</div>
    <label class="form-label mt-2">Quantity</label>
    <input type="text" class="form-control" id="fridge-send-qty" placeholder="e.g. 500 г"
           onkeydown="if(event.key==='Enter'){event.preventDefault();sendFridgeToShoppingList();}"/>
    <button class="btn btn-mm-primary w-100 mt-3" onclick="sendFridgeToShoppingList()">
      <i class="bi bi-send me-1"></i>Send</button>
  </div>
</div>

<div id="toast"></div>

<script>
const API = '';

// ── sidebar toggle ─────────────────────────────────────────────────────────
function toggleSidebar() {
  const sb = document.getElementById('sidebar');
  const ov = document.getElementById('sidebar-overlay');
  const isMobile = window.innerWidth < 768;
  if (isMobile) {
    const open = sb.classList.toggle('mobile-open');
    ov.classList.toggle('show', open);
  } else {
    sb.classList.toggle('collapsed');
  }
}
function closeSidebar() {
  document.getElementById('sidebar').classList.remove('mobile-open');
  document.getElementById('sidebar-overlay').classList.remove('show');
}
// Close mobile sidebar when a nav link is clicked
document.getElementById('sidebar-nav').addEventListener('click', () => {
  if (window.innerWidth < 768) closeSidebar();
});

// ── navigation ────────────────────────────────────────────────────────────
function showSection(name) {
  document.querySelectorAll('.mm-section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('#sidebar-nav .nav-link').forEach(b => b.classList.remove('active'));
  document.getElementById('section-' + name).classList.add('active');
  document.getElementById('nav-' + name).classList.add('active');
  if (name === 'log')        loadLog();
  if (name === 'viz')        loadViz();
  if (name === 'rec')        { setDefaultRecDate(); loadRecExcludeSettings(); }
  if (name === 'recipes')    loadRecipes();
  if (name === 'snacks')     loadSnacks();
  if (name === 'shopping')   loadShoppingList();
  if (name === 'weeklymenu') loadWeeklyMenu();
  if (name === 'fridge')    loadFridge();
  if (name === 'family')    loadFamily();
}

// ── toast ─────────────────────────────────────────────────────────────────
function toast(msg, isError = false) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.className = 'show' + (isError ? ' error' : '');
  setTimeout(() => t.className = '', 3200);
}

// ── helpers ───────────────────────────────────────────────────────────────
async function api(method, path, body) {
  const opts = { method, headers: {'Content-Type':'application/json'} };
  if (body) opts.body = JSON.stringify(body);
  const r = await fetch(API + path, opts);
  if (r.status === 401) { showAuthOverlay(); return null; }
  const data = await r.json();
  if (!r.ok) throw new Error(data.error || JSON.stringify(data));
  return data;
}

// Shared toast text for any /shopping/bulk response — mentions how many
// ingredients were already covered by the Fridge, if any.
function _shoppingAddedToast(res) {
  const fridgeNote = res.from_fridge ? ` (${res.from_fridge} already in your Fridge)` : '';
  return `Added ${res.added} ingredient(s) to Shopping List${fridgeNote}.`;
}

// ── AUTH ──────────────────────────────────────────────────────────────────
let _currentUser = null;

function showAuthOverlay() {
  document.getElementById('auth-overlay').classList.remove('hidden');
}
function hideAuthOverlay() {
  document.getElementById('auth-overlay').classList.add('hidden');
}
function authTab(tab) {
  ['login','register','forgot'].forEach(t => {
    document.getElementById('tab-' + t)?.classList.toggle('active', t === tab);
    document.getElementById('form-' + t)?.classList.toggle('active', t === tab);
  });
  // tab-forgot has no tab button, just the form
  if (tab === 'forgot') {
    document.getElementById('tab-login').classList.remove('active');
    document.getElementById('tab-register').classList.remove('active');
  }
  _authClearError();
}
function _authError(msg) {
  const el = document.getElementById('auth-error');
  el.textContent = msg; el.style.display = 'block';
}
function _authClearError() {
  const el = document.getElementById('auth-error');
  el.textContent = ''; el.style.display = 'none';
}

async function doLogin() {
  _authClearError();
  const username = document.getElementById('login-user').value.trim();
  const password = document.getElementById('login-pass').value;
  if (!username || !password) { _authError('Please fill in all fields.'); return; }
  try {
    const data = await fetch('/auth/login', {
      method: 'POST', headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ username, password }),
    });
    const json = await data.json();
    if (!data.ok) { _authError(json.error || 'Login failed.'); return; }
    _currentUser = json.user;
    _onLoginSuccess();
  } catch(e) { _authError('Connection error.'); }
}

async function doRegister() {
  _authClearError();
  const username = document.getElementById('reg-user').value.trim();
  const email    = document.getElementById('reg-email').value.trim();
  const password = document.getElementById('reg-pass').value;
  if (!username || !email || !password) { _authError('Please fill in all fields.'); return; }
  try {
    const data = await fetch('/auth/register', {
      method: 'POST', headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ username, email, password }),
    });
    const json = await data.json();
    if (!data.ok) { _authError(json.error || 'Registration failed.'); return; }
    _currentUser = json.user;
    _onLoginSuccess();
  } catch(e) { _authError('Connection error.'); }
}

async function doForgot() {
  _authClearError();
  const email = document.getElementById('forgot-email').value.trim();
  if (!email) { _authError('Please enter your email.'); return; }
  try {
    const data = await fetch('/auth/forgot-password', {
      method: 'POST', headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ email }),
    });
    const json = await data.json();
    _authClearError();
    document.getElementById('form-forgot').innerHTML =
      `<div class="alert alert-success" style="font-size:13px">${json.message}</div>
       <div class="text-center mt-2"><span class="auth-link" onclick="authTab('login')">← Back to login</span></div>`;
  } catch(e) { _authError('Connection error.'); }
}

async function doLogout() {
  try { await fetch('/auth/logout', { method: 'POST' }); } catch(e) {}
  _currentUser = null;
  showAuthOverlay();
  authTab('login');
}

function _onLoginSuccess() {
  hideAuthOverlay();
  document.getElementById('user-bar-name').textContent = _currentUser.username;
  // Reload all data for the newly logged-in user
  loadLog();
  loadRecipes();
  loadViz();
  loadShoppingList();
  loadSnacks();
  loadWeeklyMenu();
  loadFridge();
  loadFamily();
  loadIngredientUnits();
}

async function _checkSession() {
  try {
    const r = await fetch('/auth/me');
    if (r.status === 401) { showAuthOverlay(); return; }
    const data = await r.json();
    _currentUser = data.user;
    document.getElementById('user-bar-name').textContent = _currentUser.username;
    hideAuthOverlay();
    loadIngredientUnits();
  } catch(e) { showAuthOverlay(); }
}

// ── FAMILY ────────────────────────────────────────────────────────────────
async function loadFamily() {
  try {
    const data = await api('GET', '/family/');
    if (!data) return;
    const group = data.group;
    const el          = document.getElementById('family-content');
    const createPanel = document.getElementById('family-create-panel');
    const invitePanel = document.getElementById('family-invite-panel');
    const acceptPanel = document.getElementById('family-accept-panel');

    // Hide all panels first
    createPanel.style.display = 'none';
    invitePanel.style.display = 'none';
    acceptPanel.style.display = 'none';

    // No group at all → offer to create one
    if (!group) {
      el.innerHTML = '<p class="empty">You are not in a family group yet.</p>';
      createPanel.style.display = 'block';
      return;
    }

    // Find my own membership record
    const me = group.members.find(m => m.id === _currentUser.id);

    // I have a PENDING invite → show accept panel prominently, hide everything else
    if (me && me.status === 'pending') {
      const ownerMember = group.members.find(m => m.id === group.owner_id);
      const ownerName   = ownerMember ? ownerMember.username : 'someone';
      el.innerHTML = `
        <div class="alert" style="background:#3d2e0a;border:1px solid var(--mm-yellow);border-radius:10px;padding:16px 20px;color:#e2e8f0">
          <strong style="color:var(--mm-yellow)">📨 Pending invite</strong><br>
          <span style="font-size:14px"><strong>${escHtml(ownerName)}</strong> invited you to join the <strong>${escHtml(group.name)}</strong> family group.</span>
        </div>`;
      acceptPanel.style.display = 'block';
      return;
    }

    // I am an active member → show the group
    const isOwner = group.owner_id === _currentUser.id;
    let html = `<h5 class="mb-3">${escHtml(group.name)}</h5><div class="mb-3">`;
    group.members.forEach(m => {
      const isSelf = m.id === _currentUser.id;
      html += `<div class="family-member-row">
        <div class="family-member-info">
          <div class="family-member-name">${escHtml(m.username)}${isSelf ? ' <span style="font-size:11px;color:var(--mm-muted)">(you)</span>' : ''}</div>
          <div class="family-member-email">${escHtml(m.email)}</div>
        </div>
        <span class="family-status-badge status-${m.status}">${m.status}</span>
        ${isOwner && !isSelf ? `<button class="btn-icon" onclick="familyRemove(${m.id})" title="Remove member"><i class="bi bi-x-lg"></i></button>` : ''}
      </div>`;
    });
    html += '</div>';
    html += `<button class="btn btn-sm btn-mm-danger mt-2" onclick="familyLeave()">
      <i class="bi bi-door-open me-1"></i>${isOwner ? 'Disband group' : 'Leave group'}</button>`;
    el.innerHTML = html;

    // Only the owner can invite more people
    if (isOwner) invitePanel.style.display = 'block';

  } catch(e) { toast('Error loading family: ' + e.message, true); }
}

async function familyCreate() {
  const name = document.getElementById('family-group-name').value.trim() || 'Family';
  try {
    await api('POST', '/family/create', { name });
    toast('Family group created!');
    loadFamily();
  } catch(e) { toast('Error: ' + e.message, true); }
}

async function familyInvite() {
  const email = document.getElementById('family-invite-email').value.trim();
  if (!email) { toast('Enter an email address.', true); return; }
  try {
    const r = await api('POST', '/family/invite', { email });
    if (!r) return;
    toast(`Invite sent to ${r.invited}. They must accept in their Family tab.`);
    document.getElementById('family-invite-email').value = '';
    loadFamily();
  } catch(e) { toast('Error: ' + e.message, true); }
}

async function familyAccept() {
  try {
    await api('POST', '/family/accept', {});
    toast('You joined the family group! Data is now shared.');
    loadFamily();
    // Reload all data since it now comes from the group owner
    loadLog(); loadRecipes(); loadViz(); loadShoppingList(); loadSnacks(); loadWeeklyMenu();
  } catch(e) { toast('Error: ' + e.message, true); }
}

async function familyLeave() {
  if (!confirm('Are you sure you want to leave/disband the family group?')) return;
  try {
    await api('POST', '/family/leave', {});
    toast('Left the family group.');
    loadFamily();
  } catch(e) { toast('Error: ' + e.message, true); }
}

async function familyRemove(userId) {
  if (!confirm('Remove this member from the family group?')) return;
  try {
    await api('DELETE', `/family/member/${userId}`);
    toast('Member removed.');
    loadFamily();
  } catch(e) { toast('Error: ' + e.message, true); }
}

function fmtDate(iso) {
  const d = new Date(iso + 'T00:00:00');
  return d.toLocaleDateString('en-GB', {weekday:'long', year:'numeric', month:'short', day:'numeric'});
}
function today() { return _localIso(new Date()); }
function escHtml(str) {
  return String(str)
    .replace(/&/g,'&amp;').replace(/</g,'&lt;')
    .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

// ── meal type multi-select dropdown (used by Recipes: Add + Edit) ─────────
const MEAL_TYPE_LABELS = {breakfast:'🌅 Breakfast', lunch:'☀️ Lunch', dinner:'🌙 Dinner', snack:'🍎 Snack'};

function mealTypeDropdownHtml(prefix, selected) {
  selected = selected && selected.length ? selected : ['breakfast'];
  const label = selected.map(t => MEAL_TYPE_LABELS[t] || t).join(', ');
  return `<div class="ms-dropdown-wrap">
    <button type="button" class="form-select text-start" id="${prefix}-toggle" onclick="event.stopPropagation();toggleMealTypeDropdown('${prefix}')">
      <span id="${prefix}-label">${label}</span>
    </button>
    <div class="ms-dropdown-menu" id="${prefix}-menu" style="display:none">
      ${Object.entries(MEAL_TYPE_LABELS).map(([val, lbl]) => `
        <label class="ms-dropdown-item">
          <input type="checkbox" value="${val}" ${selected.includes(val)?'checked':''}
                 onchange="onMealTypeChange('${prefix}')"/> ${lbl}
        </label>`).join('')}
    </div>
  </div>`;
}

function toggleMealTypeDropdown(prefix) {
  const menu = document.getElementById(prefix + '-menu');
  const open = menu.style.display !== 'none';
  document.querySelectorAll('.ms-dropdown-menu').forEach(m => m.style.display = 'none');
  menu.style.display = open ? 'none' : 'block';
}
document.addEventListener('click', e => {
  if (!e.target.closest('.ms-dropdown-wrap')) {
    document.querySelectorAll('.ms-dropdown-menu').forEach(m => m.style.display = 'none');
  }
});

function getMealTypes(prefix) {
  return Array.from(document.querySelectorAll(`#${prefix}-menu input[type=checkbox]:checked`)).map(cb => cb.value);
}

function onMealTypeChange(prefix) {
  const types = getMealTypes(prefix);
  const label = document.getElementById(prefix + '-label');
  label.textContent = types.length ? types.map(t => MEAL_TYPE_LABELS[t]).join(', ') : 'Select meal type(s)';
}

// ── cooking method checkboxes (Recipes: Add + Edit) ────────────────────────
const METHOD_LABELS = {air_fryer: '🔥 Air Fryer', instant_pot: '⏱️ Instant Pot'};

function methodCheckboxesHtml(prefix, selected) {
  selected = selected || [];
  return Object.entries(METHOD_LABELS).map(([val, lbl]) => `
    <label class="method-check-label">
      <input type="checkbox" class="method-cb-${prefix}" value="${val}" ${selected.includes(val)?'checked':''}/> ${lbl}
    </label>`).join('');
}

function getMethods(prefix) {
  return Array.from(document.querySelectorAll(`.method-cb-${prefix}:checked`)).map(cb => cb.value);
}

// ── ingredient unit convention (shared across Add Meal, Recipes, Fridge, Shopping List) ──
let _ingredientUnits = {};

async function loadIngredientUnits() {
  try {
    _ingredientUnits = await api('GET', '/ingredients/units') || {};
  } catch(e) { _ingredientUnits = {}; }
}

// Extracts the unit portion of a free-text quantity, e.g. '3 бр' -> 'бр',
// '1/2 ч.л' -> 'ч.л', '200' -> '' (no unit). Mirrors the backend's parser.
function _parseUnit(qty) {
  const m = (qty || '').trim().match(/^-?(?:\d+\/\d+|\d+(?:[.,]\d+)?)\s*(.*)$/);
  return m ? m[1].trim().toLowerCase() : null;
}

// Call on an ingredient-name field's input event: if it matches a known
// ingredient and the paired quantity field is still empty, pre-fill just the
// unit (cursor placed before it) so typing a number completes it naturally.
function suggestIngredientUnit(nameEl, qtyEl) {
  if (!qtyEl || qtyEl.value.trim()) return;
  const unit = _ingredientUnits[nameEl.value.trim().toLowerCase()];
  if (!unit) return;
  qtyEl.value = ' ' + unit;
  if (document.activeElement === qtyEl && qtyEl.setSelectionRange) qtyEl.setSelectionRange(0, 0);
}

// Call on a quantity field's blur event: if its unit differs from the
// ingredient's known convention, confirm whether to adopt the new unit
// everywhere (retroactively renaming it across recipes, meals, the fridge,
// and the shopping list) or revert this entry back to the known unit.
async function checkIngredientUnit(nameEl, qtyEl) {
  const name = nameEl.value.trim().toLowerCase();
  const known = _ingredientUnits[name];
  if (!known) return;
  const typed = _parseUnit(qtyEl.value);
  if (!typed || typed === known.toLowerCase()) return;
  const m = qtyEl.value.trim().match(/^(-?(?:\d+\/\d+|\d+(?:[.,]\d+)?))\s*(.*)$/);
  const rawUnit = m ? m[2].trim() : typed;
  const keep = confirm(
    `You've previously used "${known}" for "${nameEl.value.trim()}". Change it to "${rawUnit}" everywhere (recipes, meals, fridge, shopping list)?`
  );
  if (!keep) {
    qtyEl.value = m ? `${m[1]} ${known}` : known;
    return;
  }
  _ingredientUnits[name] = rawUnit;
  try {
    const res = await api('POST', '/ingredients/units/rename',
      { name: nameEl.value.trim(), old_unit: known, new_unit: rawUnit });
    if (res && res.changed) {
      toast(`Updated ${res.changed} other place(s) to use "${rawUnit}" for "${nameEl.value.trim()}".`);
    }
  } catch(e) { /* best-effort — this entry already has the typed unit either way */ }
}

// ── ADD MEAL ──────────────────────────────────────────────────────────────
document.getElementById('f-date').value = today();

let _acMeals = [], _acIdx = -1;

async function _loadAcMeals() {
  if (_acMeals.length) return;
  try {
    const [templates, summaries] = await Promise.all([
      api('GET', '/templates/'), api('GET', '/meals/'),
    ]);
    const seen = {};
    templates.forEach(t => { seen[t.name] = t; });
    const byName = {};
    summaries.forEach(m => { if (!seen[m.name]) byName[m.name] = m.id; });
    if (Object.keys(byName).length) {
      const details = await Promise.all(Object.values(byName).map(id => api('GET', `/meals/${id}`)));
      details.forEach(m => {
        if (!seen[m.name] || m.products.length > (seen[m.name].products||[]).length) seen[m.name] = m;
      });
    }
    _acMeals = Object.values(seen).sort((a,b) => a.name.localeCompare(b.name));
  } catch(e) {}
}

function acInput(val) {
  _loadAcMeals();
  const list = document.getElementById('ac-list');
  const q = val.trim().toLowerCase();
  const matches = q ? _acMeals.filter(m => m.name.toLowerCase().includes(q)) : _acMeals;
  if (!matches.length) { list.style.display = 'none'; return; }
  const badgeColors = {breakfast:'background:#3d2e0a;color:#fbbf24', lunch:'background:#0d2e1a;color:#34d399', dinner:'background:#0d1a3d;color:#6c8ef5', snack:'background:#2a1a3d;color:#c084fc'};
  list.innerHTML = matches.map((m, i) =>
    `<div class="autocomplete-item" data-idx="${i}" onmousedown="acSelect(${i})">
       <span class="ac-badge" style="${badgeColors[m.meal_type]}">${m.meal_type}</span>${escHtml(m.name)}
     </div>`
  ).join('');
  list._matches = matches; _acIdx = -1; list.style.display = 'block';
}

function acSelect(idx) {
  const list = document.getElementById('ac-list');
  const m = (list._matches || [])[idx];
  if (!m) return;
  document.getElementById('f-name').value    = m.name;
  document.getElementById('f-type').value    = m.meal_type;
  document.getElementById('f-notes').value   = m.notes  || '';
  document.getElementById('f-recipe').value  = m.recipe || '';
  document.getElementById('f-calories').value = (m.calories !== undefined && m.calories !== null) ? m.calories : '';
  document.getElementById('product-list').innerHTML = '';
  (m.products || []).forEach(p => addProductRow(p.name, p.quantity));
  if (!m.products || !m.products.length) addProductRow();
  list.style.display = 'none'; _acIdx = -1;
  toast('✔ Autofilled — adjust and save!');
}

function acKeydown(e) {
  const list = document.getElementById('ac-list');
  if (list.style.display === 'none') return;
  const items = list.querySelectorAll('.autocomplete-item');
  if (e.key === 'ArrowDown') { e.preventDefault(); _acIdx = Math.min(_acIdx+1, items.length-1); }
  else if (e.key === 'ArrowUp') { e.preventDefault(); _acIdx = Math.max(_acIdx-1, 0); }
  else if (e.key === 'Enter' && _acIdx >= 0) { e.preventDefault(); acSelect(_acIdx); return; }
  else if (e.key === 'Escape') { list.style.display = 'none'; return; }
  items.forEach((el, i) => el.classList.toggle('selected', i === _acIdx));
  if (items[_acIdx]) items[_acIdx].scrollIntoView({block:'nearest'});
}

document.addEventListener('click', e => {
  if (!e.target.closest('.autocomplete-wrap')) {
    document.getElementById('ac-list').style.display = 'none';
    document.querySelectorAll('.autocomplete-list').forEach(el => el.style.display = 'none');
  }
});

function addProductRow(name='', qty='') {
  const list = document.getElementById('product-list');
  const row = document.createElement('div');
  row.className = 'product-row';
  row.innerHTML = `
    <input type="text" class="form-control p-name" placeholder="Ingredient name" value="${escHtml(name)}"
           oninput="suggestIngredientUnit(this, this.nextElementSibling)"/>
    <input type="text" class="form-control p-qty"  placeholder="Qty (e.g. 200g)" value="${escHtml(qty)}"
           onblur="checkIngredientUnit(this.previousElementSibling, this)"/>
    <button class="btn-icon" onclick="this.parentElement.remove()" title="Remove">✕</button>`;
  list.appendChild(row);
}

function resetForm() {
  document.getElementById('f-name').value     = '';
  document.getElementById('f-date').value     = today();
  document.getElementById('f-type').value     = 'breakfast';
  document.getElementById('f-notes').value    = '';
  document.getElementById('f-recipe').value   = '';
  document.getElementById('f-calories').value = '';
  document.getElementById('product-list').innerHTML = '';
  document.getElementById('ac-list').style.display = 'none';
  addProductRow(); _acMeals = [];
}

async function submitMeal() {
  const name     = document.getElementById('f-name').value.trim();
  const date     = document.getElementById('f-date').value;
  const type     = document.getElementById('f-type').value;
  const notes    = document.getElementById('f-notes').value.trim();
  const recipe   = document.getElementById('f-recipe').value.trim();
  const caloriesRaw = document.getElementById('f-calories').value;
  const calories = caloriesRaw === '' ? null : Number(caloriesRaw);
  if (!name) { toast('Please enter a meal name', true); return; }
  if (!date) { toast('Please pick a date', true); return; }
  const products = [];
  document.querySelectorAll('#product-list .product-row').forEach(row => {
    const n = row.querySelector('.p-name').value.trim();
    const q = row.querySelector('.p-qty').value.trim();
    if (n) products.push({name: n, quantity: q});
  });
  try {
    await api('POST', '/meals/', {name, meal_type: type, meal_date: date, products, notes, recipe, calories});
    toast('✔ Meal saved!'); resetForm();
  } catch(e) { toast(e.message, true); }
}

// ── MEAL LOG ──────────────────────────────────────────────────────────────
async function loadLog() {
  const dateFilter = document.getElementById('filter-date').value;
  const path = dateFilter ? `/meals/?meal_date=${dateFilter}` : '/meals/';
  const el = document.getElementById('log-content');
  el.innerHTML = '<p class="empty">Loading…</p>';
  try {
    const meals = await api('GET', path);
    if (!meals.length) { el.innerHTML = '<p class="empty">No meals found.</p>'; return; }
    const groups = {};
    meals.forEach(m => { if (!groups[m.meal_date]) groups[m.meal_date] = []; groups[m.meal_date].push(m); });
    const order = {breakfast:0, lunch:1, dinner:2, snack:3};
    let html = '';
    Object.keys(groups).sort().reverse().forEach(d => {
      const dayCalories = groups[d].reduce((sum, m) => sum + (typeof m.calories === 'number' ? m.calories : 0), 0);
      const dayCalLabel = dayCalories > 0
        ? ` <span style="color:var(--mm-accent);text-transform:none;letter-spacing:0">— ${dayCalories.toLocaleString()} kcal</span>` : '';
      html += `<div class="mb-4"><div class="date-label">${fmtDate(d)}${dayCalLabel}</div>`;
      groups[d].sort((a,b) => order[a.meal_type] - order[b.meal_type]).forEach(m => {
        const badge = `<span class="meal-type-badge badge-${m.meal_type}">${m.meal_type}</span>`;
        const products = m.products
          ? m.products.map(p => p.quantity ? `${p.name} (${p.quantity})` : p.name).join(', ')
          : (m.product_count !== undefined ? `${m.product_count} ingredient(s)` : '');
        const notes = m.notes ? `<div class="meal-notes">${escHtml(m.notes)}</div>` : '';
        const calories = (typeof m.calories === 'number')
          ? `<div class="meal-notes" style="color:var(--mm-accent2)">${m.calories.toLocaleString()} kcal</div>` : '';
        html += `<div class="meal-card">
          ${badge}
          <div class="meal-info">
            <div class="meal-name">${escHtml(m.name)}</div>
            ${products ? `<div class="meal-products">${escHtml(products)}</div>` : ''}
            ${calories}
            ${notes}
          </div>
          <div class="d-flex gap-1">
            <button class="btn btn-sm btn-mm-danger" onclick="deleteMeal(${m.id}, this)">Delete</button>
          </div>
        </div>`;
      });
      html += '</div>';
    });
    el.innerHTML = html;
  } catch(e) { el.innerHTML = `<p class="empty" style="color:var(--mm-red)">${e.message}</p>`; }
}

async function deleteMeal(id, btn) {
  if (!confirm('Delete this meal?')) return;
  try {
    await api('DELETE', `/meals/${id}`);
    toast('Meal deleted');
    btn.closest('.meal-card').remove();
  } catch(e) { toast(e.message, true); }
}

// ── VISUALISE ─────────────────────────────────────────────────────────────
function onVizRangeChange() {
  const isCustom = document.getElementById('viz-range').value === 'custom';
  ['viz-custom-start', 'viz-custom-sep', 'viz-custom-end', 'viz-custom-apply'].forEach(id => {
    document.getElementById(id).style.display = isCustom ? '' : 'none';
  });
  if (!isCustom) loadViz();
}

// Inclusive list of ISO date strings from start to end.
function _dateRange(start, end) {
  const dates = [];
  const d = new Date(start + 'T00:00:00');
  const endD = new Date(end + 'T00:00:00');
  while (d <= endD) {
    dates.push(_localIso(d));
    d.setDate(d.getDate() + 1);
  }
  return dates;
}

async function loadViz() {
  const el = document.getElementById('viz-content');
  el.innerHTML = '<p class="empty">Loading…</p>';
  try {
    const summaries = await api('GET', '/meals/');
    if (!summaries.length) { el.innerHTML = '<p class="empty">No meals yet — add some first.</p>'; return; }
    const range = document.getElementById('viz-range').value;
    const end   = today();
    let start, rangeEnd = end;
    if (range === 'all') {
      start = summaries.reduce((min, m) => m.meal_date < min ? m.meal_date : min, summaries[0].meal_date);
    } else if (range === 'custom') {
      start = document.getElementById('viz-custom-start').value;
      if (!start) { el.innerHTML = '<p class="empty">Pick a start date.</p>'; return; }
      rangeEnd = document.getElementById('viz-custom-end').value || end;
    } else {
      start = _localIso(new Date(Date.now() - Number(range)*86400000));
    }
    const recent = await api('GET', `/meals/range?start=${start}&end=${rangeEnd}`);
    el.innerHTML = `
      <div class="col-12 col-lg-6">${chartTypeDistribution(recent)}</div>
      <div class="col-12 col-lg-6">${chartHeatmap(recent, start, rangeEnd)}</div>
      <div class="col-12 col-lg-6">${chartTopIngredients(recent)}</div>
      <div class="col-12 col-lg-6">${chartDiversity(recent, start, rangeEnd)}</div>`;
  } catch(e) { el.innerHTML = `<p class="empty" style="color:var(--mm-red)">${e.message}</p>`; }
}

function _chartCard(title, body) {
  return `<div class="mm-card h-100"><h6 class="text-info mb-3">${title}</h6>${body}</div>`;
}

function chartTypeDistribution(meals) {
  const counts = {breakfast:0, lunch:0, dinner:0, snack:0};
  meals.forEach(m => { if (counts[m.meal_type] !== undefined) counts[m.meal_type]++; });
  const total = meals.length || 1;
  const colors = {breakfast:'var(--mm-yellow)', lunch:'var(--mm-green)', dinner:'var(--mm-accent)', snack:'#c084fc'};
  let rows = '';
  for (const [t, n] of Object.entries(counts)) {
    const pct = Math.round(n/total*100);
    rows += `<div class="bar-row">
      <div class="bar-label">${t}</div>
      <div class="bar-track"><div class="bar-fill" style="width:${pct}%;background:${colors[t]}"></div></div>
      <div class="bar-val">${n}</div></div>`;
  }
  return _chartCard('Meal-type distribution', rows);
}

function chartHeatmap(meals, start, end) {
  const byDay = {};
  meals.forEach(m => {
    if (!byDay[m.meal_date]) byDay[m.meal_date] = { types: new Set(), calories: 0 };
    byDay[m.meal_date].types.add(m.meal_type);
    if (typeof m.calories === 'number') byDay[m.meal_date].calories += m.calories;
  });
  const dates = _dateRange(start, end);
  const todayStr = today();
  let totalCalories = 0, daysWithCalories = 0;
  let rows = '';
  for (let i = dates.length - 1; i >= 0; i--) {
    const d = dates[i];
    const day = byDay[d] || { types: new Set(), calories: 0 };
    const label = d.slice(5);
    const b  = `<div class="dot dot-b ${day.types.has('breakfast')?'dot-on':'dot-off'}">B</div>`;
    const l  = `<div class="dot dot-l ${day.types.has('lunch')    ?'dot-on':'dot-off'}">L</div>`;
    const dn = `<div class="dot dot-d ${day.types.has('dinner')   ?'dot-on':'dot-off'}">D</div>`;
    const marker = d === todayStr ? ' <span style="color:var(--mm-accent);font-size:10px">today</span>' : '';
    const cal = day.calories > 0 ? `<span class="heatmap-cal">${day.calories.toLocaleString()} kcal</span>` : '';
    if (day.calories > 0) { totalCalories += day.calories; daysWithCalories++; }
    rows += `<div class="heatmap-row"><div class="heatmap-date">${label}${marker}</div>${b}${l}${dn}${cal}</div>`;
  }
  const summary = daysWithCalories
    ? `<p style="font-size:12px;color:var(--mm-muted);margin-bottom:10px">
         ${totalCalories.toLocaleString()} kcal logged over ${daysWithCalories} day(s) — avg
         ${Math.round(totalCalories/daysWithCalories).toLocaleString()} kcal/day</p>`
    : '';
  return _chartCard(`Daily coverage — ${dates.length} day(s)`,
    `${summary}<div style="max-height:420px;overflow-y:auto">${rows}</div>`);
}

function chartTopIngredients(meals) {
  const counts = {};
  meals.forEach(m => (m.products||[]).forEach(p => { const k = p.name.toLowerCase(); counts[k] = (counts[k]||0)+1; }));
  const sorted = Object.entries(counts).sort((a,b)=>b[1]-a[1]).slice(0,10);
  if (!sorted.length) return _chartCard('Top ingredients', '<p class="empty">No ingredient data.</p>');
  const max = sorted[0][1];
  const rows = sorted.map(([n,c]) => `<div class="bar-row">
    <div class="bar-label">${escHtml(n)}</div>
    <div class="bar-track"><div class="bar-fill" style="width:${Math.round(c/max*100)}%;background:var(--mm-accent2)"></div></div>
    <div class="bar-val">${c}</div></div>`).join('');
  return _chartCard('Top 10 ingredients', rows);
}

function chartDiversity(meals, start, end) {
  const byDay = {};
  meals.forEach(m => { if (!byDay[m.meal_date]) byDay[m.meal_date] = []; (m.products||[]).forEach(p => byDay[m.meal_date].push(p.name.toLowerCase())); });
  const dates = _dateRange(start, end);
  const todayStr = today();
  let rows = '';
  for (let i = dates.length - 1; i >= 0; i--) {
    const d = dates[i];
    const prods = byDay[d] || [];
    const score = prods.length ? (new Set(prods).size / prods.length) : 0;
    const pct   = Math.round(score * 100);
    const color = score > .8 ? 'var(--mm-green)' : score > .5 ? 'var(--mm-yellow)' : 'var(--mm-red)';
    const marker = d === todayStr ? ' <span style="color:var(--mm-accent);font-size:10px">today</span>' : '';
    rows += `<div class="bar-row">
      <div class="bar-label" style="width:60px">${d.slice(5)}${marker}</div>
      <div class="bar-track"><div class="bar-fill" style="width:${pct}%;background:${color}"></div></div>
      <div class="bar-val">${pct}%</div></div>`;
  }
  return _chartCard(`Diversity trend — ${dates.length} day(s)`,
    `<div style="max-height:420px;overflow-y:auto">${rows}</div>`);
}

// ── RECOMMEND ─────────────────────────────────────────────────────────────
let _recMode = 'day', _lastRecData = null;

function setRecMode(mode) {
  _recMode = mode;
  document.getElementById('rec-mode-day').className    = 'btn btn-sm ' + (mode==='day'    ? 'btn-mm-primary' : 'btn-mm-secondary');
  document.getElementById('rec-mode-week').className   = 'btn btn-sm ' + (mode==='week'   ? 'btn-mm-primary' : 'btn-mm-secondary');
  document.getElementById('rec-mode-config').className = 'btn btn-sm ' + (mode==='config' ? 'btn-mm-primary' : 'btn-mm-secondary');
  document.getElementById('rec-config-panel').style.display   = mode === 'config' ? '' : 'none';
  document.getElementById('rec-day-week-panel').style.display = mode === 'config' ? 'none' : '';
  if (mode === 'config') { loadRecExcludeSettings(); return; }
  document.getElementById('rec-date-label').textContent = mode === 'week' ? 'Week starting:' : 'Target date:';
  setDefaultRecDate();
}

function setDefaultRecDate() {
  const el = document.getElementById('rec-date');
  if (!el.value) el.value = _localIso(new Date(Date.now() + 86400000));
}

function _recBtnsShow(show) {
  document.getElementById('rec-export-btn').style.display = show ? '' : 'none';
  document.getElementById('rec-to-wm-btn').style.display  = show ? '' : 'none';
}

// ── excluded ingredients (saved server-side, applied to every recommendation) ──
let _recExcludeList = [];

async function loadRecExcludeSettings() {
  try {
    const res = await api('GET', '/recommendations/settings');
    _recExcludeList = res.excluded_ingredients || [];
  } catch(e) { _recExcludeList = []; }
  renderRecExcludeTags();
}

function renderRecExcludeTags() {
  const el = document.getElementById('rec-exclude-tags');
  _recExcludeList.sort((a, b) => a.toLowerCase().localeCompare(b.toLowerCase()));
  if (!_recExcludeList.length) {
    el.innerHTML = '<span style="font-size:12px;color:var(--mm-muted);font-style:italic">No exclusions yet.</span>';
    return;
  }
  el.innerHTML = _recExcludeList.map(name => `
    <span class="tag" style="display:inline-flex;align-items:center;gap:6px">
      ${escHtml(name)}
      <button class="btn-icon" style="padding:0;font-size:11px;line-height:1"
              onclick="removeRecExclude('${escHtml(name).replace(/'/g,"\\'")}')" title="Remove">✕</button>
    </span>`).join('');
}

async function saveRecExcludeSettings() {
  try {
    await api('PUT', '/recommendations/settings', { excluded_ingredients: _recExcludeList });
  } catch(e) { toast('Error saving exclusions: ' + e.message, true); }
}

function addRecExclude() {
  const input = document.getElementById('rec-exclude-input');
  const name  = input.value.trim();
  if (!name) return;
  if (!_recExcludeList.some(n => n.toLowerCase() === name.toLowerCase())) {
    _recExcludeList.push(name);
    renderRecExcludeTags();
    saveRecExcludeSettings();
  }
  input.value = '';
}

function removeRecExclude(name) {
  _recExcludeList = _recExcludeList.filter(n => n.toLowerCase() !== name.toLowerCase());
  renderRecExcludeTags();
  saveRecExcludeSettings();
}

async function loadRec() {
  if (_recMode === 'week') { await loadRecWeek(); return; }
  const d    = document.getElementById('rec-date').value;
  const path = '/recommendations/next-day' + (d ? `?target_date=${d}` : '');
  const el   = document.getElementById('rec-content');
  el.innerHTML = '<p class="empty">Thinking…</p>';
  _recBtnsShow(false);
  try {
    const rec = await api('GET', path);
    _lastRecData = { mode: 'day', data: rec };
    el.innerHTML = renderDayRec(rec.target_date, rec);
    _recBtnsShow(true);
  } catch(e) { el.innerHTML = `<p class="empty" style="color:var(--mm-red)">${e.message}</p>`; }
}

async function loadRecWeek() {
  const d    = document.getElementById('rec-date').value;
  const path = '/recommendations/week' + (d ? `?start_date=${d}` : '');
  const el   = document.getElementById('rec-content');
  el.innerHTML = '<p class="empty">Planning your week…</p>';
  _recBtnsShow(false);
  try {
    const data = await api('GET', path);
    _lastRecData = { mode: 'week', data };
    let html = `<p class="text-muted small mb-3">Week plan: <strong class="text-light">${fmtDate(data.start_date)}</strong> → <strong class="text-light">${fmtDate(data.end_date)}</strong></p>`;
    data.days.forEach((day, i) => {
      const b = day.breakfast, l = day.lunch, dn = day.dinner;
      html += `<div class="week-day-row${i===0?' open':''}" id="wdr-${i}">
        <div class="week-day-header" onclick="toggleWeekDay('wdr-${i}')">
          <div class="week-day-name">${day.day}</div>
          <div class="week-day-date">${day.date}</div>
          <div class="week-day-pills">
            <span class="week-pill pill-b">${escHtml(b.meal_name)}</span>
            <span class="week-pill pill-l">${escHtml(l.meal_name)}</span>
            <span class="week-pill pill-d">${escHtml(dn.meal_name)}</span>
          </div>
          <div class="week-day-arrow">›</div>
        </div>
        <div class="week-day-body">${renderDayRec(day.date, day, true)}</div>
      </div>`;
    });
    el.innerHTML = html;
    _recBtnsShow(true);
  } catch(e) { el.innerHTML = `<p class="empty" style="color:var(--mm-red)">${e.message}</p>`; }
}

function toggleWeekDay(id) { document.getElementById(id).classList.toggle('open'); }

function renderDayRec(dateStr, rec, compact=false) {
  const colors = {breakfast:'var(--mm-yellow)', lunch:'var(--mm-green)', dinner:'var(--mm-accent)'};
  let html = '';
  if (!compact)
    html += `<p class="text-muted small mb-3">Recommendations for <strong class="text-light">${fmtDate(dateStr)}</strong></p>`;
  html += '<div class="row g-3">';
  for (const slot of ['breakfast','lunch','dinner']) {
    const r   = rec[slot];
    const pct = Math.round(r.diversity_score * 100);
    const tags = r.suggested_products.map(p => {
      const isObj = p && typeof p === 'object';
      const label = isObj ? (p.quantity ? `${p.name} (${p.quantity})` : p.name) : p;
      return `<span class="tag">${escHtml(label)}</span>`;
    }).join('');
    html += `<div class="col-12 col-md-4">
      <div class="rec-card h-100">
        <div class="rec-type" style="color:${colors[slot]}">${slot}</div>
        <div class="rec-name">${escHtml(r.meal_name)}</div>
        <div class="rec-score">Diversity: ${pct}%</div>
        <div class="score-bar"><div class="score-fill" style="width:${pct}%"></div></div>
        <div class="rec-reason">${escHtml(r.reason)}</div>
        <div class="rec-products">${tags}</div>
      </div></div>`;
  }
  html += '</div>';
  return html;
}

async function exportToShoppingList() {
  if (!_lastRecData) return;
  const items = [];
  const collectSlots = (day) => {
    const dateStr = day.target_date || day.date;
    for (const slot of ['breakfast','lunch','dinner']) {
      const r = day[slot];
      if (r && r.suggested_products) {
        const source = `rec:${dateStr}:${slot}`;
        r.suggested_products.forEach(p => {
          const isObj = p && typeof p === 'object';
          items.push({ item: isObj ? p.name : p, quantity: isObj ? (p.quantity || '') : '', source });
        });
      }
    }
  };
  if (_lastRecData.mode === 'day') collectSlots(_lastRecData.data);
  else _lastRecData.data.days.forEach(day => collectSlots(day));
  if (!items.length) { toast('No ingredients to add.'); return; }
  try {
    const res = await api('POST', '/shopping/bulk', { items });
    toast(_shoppingAddedToast(res));
    if (res.from_fridge) loadFridge();
    showSection('shopping');
  } catch(e) { toast('Failed to export: ' + e.message, true); }
}

// ── RECIPES ───────────────────────────────────────────────────────────────
let _allRecipes = [], _templateIds = new Set();

function toggleAddRecipePanel() {
  const panel = document.getElementById('add-recipe-panel');
  const visible = panel.style.display !== 'none';
  panel.style.display = visible ? 'none' : 'block';
  if (!visible) {
    document.getElementById('tr-name').value     = '';
    document.getElementById('tr-type-container').innerHTML = mealTypeDropdownHtml('tr-type', ['breakfast']);
    document.getElementById('tr-calories').value = '';
    document.getElementById('tr-notes').value    = '';
    document.getElementById('tr-recipe').value   = '';
    document.getElementById('tr-method-container').innerHTML = methodCheckboxesHtml('tr', []);
    document.getElementById('tr-product-list').innerHTML = '';
    addTrProductRow();
  }
}

function addTrProductRow(name='', qty='') {
  const list = document.getElementById('tr-product-list');
  const row  = document.createElement('div');
  row.className = 'product-row';
  row.innerHTML = `
    <input type="text" class="form-control p-name" placeholder="Ingredient name" value="${escHtml(name)}"
           oninput="suggestIngredientUnit(this, this.nextElementSibling)"/>
    <input type="text" class="form-control p-qty"  placeholder="Qty (e.g. 200g)" value="${escHtml(qty)}"
           onblur="checkIngredientUnit(this.previousElementSibling, this)"/>
    <button class="btn-icon" onclick="this.parentElement.remove()" title="Remove">✕</button>`;
  list.appendChild(row);
}

async function submitTemplate() {
  const name       = document.getElementById('tr-name').value.trim();
  const meal_types = getMealTypes('tr-type');
  const notes      = document.getElementById('tr-notes').value.trim();
  const recipe     = document.getElementById('tr-recipe').value.trim();
  const methods    = getMethods('tr');
  const caloriesRaw = document.getElementById('tr-calories').value;
  const calories   = caloriesRaw === '' ? null : Number(caloriesRaw);
  if (!name) { toast('Please enter a recipe name', true); return; }
  if (!meal_types.length) { toast('Please select at least one meal type', true); return; }
  const products = [];
  document.querySelectorAll('#tr-product-list .product-row').forEach(row => {
    const n = row.querySelector('.p-name').value.trim();
    const q = row.querySelector('.p-qty').value.trim();
    if (n) products.push({name: n, quantity: q});
  });
  try {
    await api('POST', '/templates/', { name, meal_types, methods, notes, recipe, calories, products });
    toast('✔ Recipe saved!');
    toggleAddRecipePanel(); _acMeals = []; loadRecipes();
  } catch(e) { toast(e.message, true); }
}

async function deleteTemplate(tid, e) {
  e.stopPropagation();
  if (!confirm('Delete this recipe template?')) return;
  try {
    await api('DELETE', `/templates/${tid}`);
    toast('Recipe deleted'); _acMeals = []; loadRecipes();
  } catch(err) { toast(err.message, true); }
}

async function deleteLoggedRecipe(mealId, e) {
  e.stopPropagation();
  if (!confirm('Delete all logged entries of this meal?')) return;
  try {
    // Delete every logged instance with this meal id
    await api('DELETE', `/meals/${mealId}`);
    toast('Meal deleted'); _acMeals = []; loadRecipes();
  } catch(err) { toast(err.message, true); }
}

async function loadRecipes() {
  const el = document.getElementById('recipes-content');
  el.innerHTML = '<p class="empty">Loading…</p>';
  try {
    const [templates, summaries] = await Promise.all([api('GET', '/templates/'), api('GET', '/meals/')]);
    _templateIds = new Set(templates.map(t => `tpl-${t.id}`));
    const tplItems = templates.map(t => ({...t, _id: `tpl-${t.id}`, _source: 'template'}));
    const tplNames = new Set(templates.map(t => t.name.toLowerCase()));
    const byName = {};
    summaries.forEach(s => { const k = s.name.toLowerCase(); if (!tplNames.has(k) && !byName[k]) byName[k] = s.id; });
    let loggedItems = [];
    if (Object.keys(byName).length) {
      const details = await Promise.all(Object.values(byName).map(id => api('GET', `/meals/${id}`)));
      const seen = {};
      details.forEach(m => { if (!seen[m.name] || (m.recipe && !seen[m.name].recipe)) seen[m.name] = m; });
      loggedItems = Object.values(seen).map(m => ({...m, _id: `meal-${m.id}`, _source: 'logged'}));
    }
    _allRecipes = [...tplItems, ...loggedItems].sort((a,b) => a.name.localeCompare(b.name));
    renderRecipes(_allRecipes);
  } catch(e) { el.innerHTML = `<p class="empty" style="color:var(--mm-red)">${e.message}</p>`; }
}

function renderRecipes(meals) {
  const el = document.getElementById('recipes-content');
  if (!meals.length) { el.innerHTML = '<p class="empty">No meals match your search.</p>'; return; }
  const badgeColors = {
    breakfast:'background:#3d2e0a;color:#fbbf24', lunch:'background:#0d2e1a;color:#34d399',
    dinner:'background:#0d1a3d;color:#6c8ef5', snack:'background:#2a1a3d;color:#c084fc',
  };
  el.innerHTML = meals.map(m => {
    const isTemplate = m._source === 'template';
    const realId = m.id, domId = m._id || `meal-${m.id}`;
    const types = (m.meal_types && m.meal_types.length) ? m.meal_types : [m.meal_type];
    const badge = `<span id="type-badges-${domId}">${types.map(t =>
      `<span class="meal-type-badge" style="${badgeColors[t]};font-size:10px;padding:2px 8px;border-radius:4px;font-weight:700;text-transform:uppercase;margin-right:3px">${t}</span>`
    ).join('')}</span>`;
    const srcBadge = isTemplate
      ? `<span style="font-size:10px;background:#1a2a1a;color:#34d399;border:1px solid #34d39940;border-radius:4px;padding:2px 7px;font-weight:600">📖 template</span>`
      : `<span style="font-size:10px;background:#1a1a2a;color:#8892a4;border:1px solid #2e335040;border-radius:4px;padding:2px 7px;font-weight:600">📋 logged</span>`;
    const calBadge = `<span id="cal-badge-${domId}">${(typeof m.calories === 'number')
      ? `<span class="tag" style="margin-left:2px">🔥 ${m.calories.toLocaleString()} kcal</span>` : ''}</span>`;
    const ingredients = (m.products && m.products.length)
      ? `<div class="recipe-section-title">Ingredients</div>
         <div class="ingredient-list" id="view-ing-${domId}">
           ${m.products.map(p => `<div class="ingredient-row"><span>${escHtml(p.name)}</span><span class="ingredient-qty">${escHtml(p.quantity||'—')}</span></div>`).join('')}
         </div>`
      : `<div class="recipe-section-title">Ingredients</div><p class="no-recipe" id="view-ing-${domId}">No ingredients listed.</p>`;
    const recipeBlock = m.recipe
      ? `<div class="recipe-section-title">Recipe</div><div class="recipe-text" id="view-rec-${domId}">${escHtml(m.recipe)}</div>`
      : `<div class="recipe-section-title">Recipe</div><p class="no-recipe" id="view-rec-${domId}">No recipe added yet.</p>`;
    const notesBlock = m.notes
      ? `<div class="recipe-section-title">Notes</div><p style="font-size:13px;color:var(--mm-accent2);font-style:italic">${escHtml(m.notes)}</p>`
      : '';
    const methodsBlock = isTemplate
      ? `<div class="recipe-section-title">Cooking Method</div>
         <div class="mb-2" id="view-methods-${domId}">${(m.methods && m.methods.length)
             ? m.methods.map(mm => `<span class="tag" style="margin-right:4px">${METHOD_LABELS[mm]||mm}</span>`).join('')
             : '<span class="no-recipe">None selected.</span>'}</div>`
      : '';
    const editIngRows = (m.products && m.products.length)
      ? m.products.map((p,i) => editIngRow(p.name, p.quantity, domId, i)).join('')
      : editIngRow('', '', domId, 0);
    const deleteBtn = isTemplate
      ? `<button class="btn btn-sm btn-mm-danger" onclick="deleteTemplate(${realId}, event)"><i class="bi bi-trash"></i> Delete</button>`
      : `<button class="btn btn-sm btn-mm-danger" onclick="deleteLoggedRecipe(${realId}, event)"><i class="bi bi-trash"></i> Delete</button>`;
    return `<div class="recipe-card" id="rc-${domId}">
      <div class="recipe-card-header" onclick="toggleRecipe('rc-${domId}')">
        <div class="recipe-card-labels">${badge} ${srcBadge} ${calBadge}</div>
        <div class="recipe-card-title" id="title-${domId}">${escHtml(m.name)}</div>
        <div class="recipe-card-arrow">›</div>
      </div>
      <div class="recipe-card-body">
        ${ingredients}${recipeBlock}${methodsBlock}${notesBlock}
        <div class="recipe-card-actions">
          <button class="btn btn-sm btn-mm-secondary" onclick="openEditPanel('${domId}',${realId},'${m._source}',event)">
            <i class="bi bi-pencil"></i> Edit</button>
          ${deleteBtn}
        </div>
        <div class="edit-panel" id="edit-panel-${domId}">
          <label>Name</label>
          <input type="text" class="form-control mb-3" id="edit-name-${domId}" value="${escHtml(m.name)}"/>
          ${isTemplate ? `<label>Meal type(s)</label>
          <div class="mb-3">${mealTypeDropdownHtml(`edit-type-${domId}`, m.meal_types || [m.meal_type])}</div>` : ''}
          <label>Calories <span style="text-transform:none;font-weight:400">(optional)</span></label>
          <input type="number" min="0" step="1" class="form-control mb-3" id="edit-calories-${domId}"
                 placeholder="e.g. 450" value="${(typeof m.calories === 'number') ? m.calories : ''}"/>
          <label>Ingredients</label>
          <div class="edit-ingredients-list" id="edit-ing-list-${domId}">${editIngRows}</div>
          <button class="btn btn-sm btn-mm-secondary mb-3" onclick="addEditIngRow('${domId}',event)">+ Add ingredient</button>
          <label>Recipe</label>
          <textarea class="form-control" id="edit-recipe-${domId}" oninput="autoGrow(this)">${escHtml(m.recipe||'')}</textarea>
          ${isTemplate ? `<label class="mt-3">Cooking method</label>
          <div class="mb-3">${methodCheckboxesHtml(`edit-${domId}`, m.methods || [])}</div>` : ''}
          <div class="d-flex gap-2 mt-3 flex-wrap">
            <button class="btn btn-sm btn-mm-primary"   onclick="saveRecipeEdit('${domId}',${realId},'${m._source}',event)">
              <i class="bi bi-floppy"></i> Save changes</button>
            <button class="btn btn-sm btn-mm-secondary" onclick="closeEditPanel('${domId}',event)">Cancel</button>
          </div>
        </div>
      </div>
    </div>`;
  }).join('');
}

function editIngRow(name, qty, domId, idx) {
  return `<div class="edit-ingredient-row" id="edit-ing-row-${domId}-${idx}">
    <input type="text" class="form-control ei-name" placeholder="Ingredient" value="${escHtml(name)}"
           oninput="suggestIngredientUnit(this, this.nextElementSibling)"/>
    <input type="text" class="form-control ei-qty"  placeholder="Qty" value="${escHtml(qty)}"
           onblur="checkIngredientUnit(this.previousElementSibling, this)"/>
    <button class="btn-icon" onclick="this.closest('.edit-ingredient-row').remove()" title="Remove">✕</button>
  </div>`;
}

let _editIngCounter = 1000;
function addEditIngRow(domId, e) {
  e.stopPropagation();
  const list = document.getElementById(`edit-ing-list-${domId}`);
  const div  = document.createElement('div');
  div.innerHTML = editIngRow('', '', domId, _editIngCounter++);
  list.appendChild(div.firstElementChild);
}

function openEditPanel(domId, realId, source, e) {
  e.stopPropagation();
  const panel = document.getElementById(`edit-panel-${domId}`);
  panel.classList.add('visible');
  const ta = document.getElementById(`edit-recipe-${domId}`);
  if (ta) autoGrow(ta);
  document.getElementById(`rc-${domId}`).classList.add('open');
}

function closeEditPanel(domId, e) {
  e.stopPropagation();
  document.getElementById(`edit-panel-${domId}`).classList.remove('visible');
}

async function saveRecipeEdit(domId, realId, source, e) {
  e.stopPropagation();
  const products = [];
  document.querySelectorAll(`#edit-ing-list-${domId} .edit-ingredient-row`).forEach(row => {
    const name = row.querySelector('.ei-name').value.trim();
    const qty  = row.querySelector('.ei-qty').value.trim();
    if (name) products.push({name, quantity: qty});
  });
  const recipe = document.getElementById(`edit-recipe-${domId}`).value.trim();
  const caloriesRaw = document.getElementById(`edit-calories-${domId}`).value;
  const calories = caloriesRaw === '' ? null : Number(caloriesRaw);
  const name = document.getElementById(`edit-name-${domId}`).value.trim();
  if (!name) { toast('Please enter a name', true); return; }
  try {
    let updated;
    if (source === 'template') {
      const cur = await api('GET', `/templates/${realId}`);
      const meal_types = getMealTypes(`edit-type-${domId}`);
      const methods    = getMethods(`edit-${domId}`);
      if (!meal_types.length) { toast('Please select at least one meal type', true); return; }
      updated = await api('PUT', `/templates/${realId}`, {
        name, meal_types, methods, calories,
        notes: cur.notes, recipe, products,
      });
    } else {
      const cur = await api('GET', `/meals/${realId}`);
      updated = await api('PUT', `/meals/${realId}`, {
        name, meal_type: cur.meal_type, calories,
        meal_date: cur.meal_date, notes: cur.notes, recipe, products,
      });
    }
    const idx = _allRecipes.findIndex(m => m._id === domId);
    if (idx !== -1) _allRecipes[idx] = {..._allRecipes[idx], ...updated};
    _acMeals = [];
    toast('✔ Changes saved!');
    closeEditPanel(domId, e);
    const titleEl = document.getElementById(`title-${domId}`);
    if (titleEl) titleEl.textContent = updated.name;
    const viewIng = document.getElementById(`view-ing-${domId}`);
    if (viewIng) viewIng.outerHTML = (updated.products && updated.products.length)
      ? `<div class="ingredient-list" id="view-ing-${domId}">${updated.products.map(p => `<div class="ingredient-row"><span>${escHtml(p.name)}</span><span class="ingredient-qty">${escHtml(p.quantity||'—')}</span></div>`).join('')}</div>`
      : `<p class="no-recipe" id="view-ing-${domId}">No ingredients listed.</p>`;
    const viewRec = document.getElementById(`view-rec-${domId}`);
    if (viewRec) viewRec.outerHTML = updated.recipe
      ? `<div class="recipe-text" id="view-rec-${domId}">${escHtml(updated.recipe)}</div>`
      : `<p class="no-recipe" id="view-rec-${domId}">No recipe added yet.</p>`;
    const badgesEl = document.getElementById(`type-badges-${domId}`);
    if (badgesEl && updated.meal_types) {
      const badgeColors = {breakfast:'background:#3d2e0a;color:#fbbf24', lunch:'background:#0d2e1a;color:#34d399', dinner:'background:#0d1a3d;color:#6c8ef5', snack:'background:#2a1a3d;color:#c084fc'};
      badgesEl.innerHTML = updated.meal_types.map(t =>
        `<span class="meal-type-badge" style="${badgeColors[t]};font-size:10px;padding:2px 8px;border-radius:4px;font-weight:700;text-transform:uppercase;margin-right:3px">${t}</span>`
      ).join('');
    }
    const methodsEl = document.getElementById(`view-methods-${domId}`);
    if (methodsEl && updated.methods !== undefined) {
      methodsEl.innerHTML = updated.methods.length
        ? updated.methods.map(mm => `<span class="tag" style="margin-right:4px">${METHOD_LABELS[mm]||mm}</span>`).join('')
        : '<span class="no-recipe">None selected.</span>';
    }
    const calBadgeEl = document.getElementById(`cal-badge-${domId}`);
    if (calBadgeEl) {
      calBadgeEl.innerHTML = (typeof updated.calories === 'number')
        ? `<span class="tag" style="margin-left:2px">🔥 ${updated.calories.toLocaleString()} kcal</span>` : '';
    }
  } catch(err) { toast(err.message, true); }
}

function toggleRecipe(id) { document.getElementById(id).classList.toggle('open'); }

// Search matches the meal name only (not ingredients, notes or recipe steps),
// combined with the cooking-method filter dropdown (All / Instant Pot / Air Fryer)
// and the meal-type filter buttons (All / Breakfast / Lunch / Dinner / Snack).
let _recipeTypeFilter = 'all';

function setRecipeTypeFilter(type) {
  _recipeTypeFilter = type;
  document.querySelectorAll('.recipe-type-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.type === type);
  });
  filterRecipes();
}

function filterRecipes() {
  const q = document.getElementById('recipe-search').value.trim().toLowerCase();
  const methods = getRecipeMethodFilter();
  let filtered = q ? _allRecipes.filter(m => m.name.toLowerCase().includes(q)) : _allRecipes;
  if (methods.length) {
    filtered = filtered.filter(m => (m.methods || []).some(mm => methods.includes(mm)));
  }
  if (_recipeTypeFilter !== 'all') {
    filtered = filtered.filter(m => {
      const types = (m.meal_types && m.meal_types.length) ? m.meal_types : [m.meal_type];
      return types.includes(_recipeTypeFilter);
    });
  }
  renderRecipes(filtered);
}

function getRecipeMethodFilter() {
  const selected = [];
  const ip = document.getElementById('rmf-instant_pot');
  const af = document.getElementById('rmf-air_fryer');
  if (ip && ip.checked) selected.push('instant_pot');
  if (af && af.checked) selected.push('air_fryer');
  return selected;
}

function onRecipeMethodFilterChange(changed) {
  const all = document.getElementById('rmf-all');
  const ip  = document.getElementById('rmf-instant_pot');
  const af  = document.getElementById('rmf-air_fryer');
  if (changed === 'all') {
    if (all.checked) { ip.checked = false; af.checked = false; }
    else if (!ip.checked && !af.checked) { all.checked = true; }
  } else {
    all.checked = !(ip.checked || af.checked);
  }
  const label = document.getElementById('recipe-method-filter-label');
  const parts = [];
  if (ip.checked) parts.push(METHOD_LABELS.instant_pot);
  if (af.checked) parts.push(METHOD_LABELS.air_fryer);
  label.textContent = parts.length ? parts.join(', ') : 'All';
  filterRecipes();
}

// ── SNACKS ────────────────────────────────────────────────────────────────
// A snack can come from two places: an actual logged meal (Add Meal, dated)
// or a snack recipe template (Recipes tab, undated) — both are shown here.
let _allSnacks = [], _allSnackTemplates = [], _snackAcIdx = -1;

async function loadSnacks() {
  const dateVal = document.getElementById('snack-filter-date').value;
  const el = document.getElementById('snack-content');
  el.innerHTML = '<p class="empty">Loading…</p>';
  try {
    const [meals, templates] = await Promise.all([
      api('GET', dateVal ? `/meals/?meal_date=${dateVal}` : '/meals/'),
      api('GET', '/templates/'),
    ]);
    _allSnacks = meals.filter(m => m.meal_type === 'snack');
    _allSnackTemplates = templates.filter(t =>
      (t.meal_types && t.meal_types.length ? t.meal_types : [t.meal_type]).includes('snack'));
    renderSnacksFiltered(document.getElementById('snack-search').value);
  } catch(e) { el.innerHTML = `<p class="empty" style="color:var(--mm-red)">${e.message}</p>`; }
}

function onSnackShowLoggedChange() {
  const showLogged = document.getElementById('snack-show-logged').checked;
  document.getElementById('snack-filter-date').style.display = showLogged ? '' : 'none';
  renderSnacksFiltered(document.getElementById('snack-search').value);
}

function renderSnacksFiltered(q) {
  q = (q || '').trim().toLowerCase();
  const showLogged = document.getElementById('snack-show-logged').checked;
  const templates = q ? _allSnackTemplates.filter(t => t.name.toLowerCase().includes(q)) : _allSnackTemplates;
  const meals = !showLogged ? [] : (q ? _allSnacks.filter(m => m.name.toLowerCase().includes(q)) : _allSnacks);
  renderSnacks(meals, templates, showLogged);
}

function renderSnacks(meals, templates, showLogged) {
  const el = document.getElementById('snack-content');
  if (!templates.length && !meals.length) {
    el.innerHTML = showLogged
      ? '<p class="empty">No snacks found.</p>'
      : '<p class="empty">No snack recipes found. Tick "Also show logged snacks" to include your Meal Log, or add one in the Recipes tab.</p>';
    return;
  }
  let html = '';

  if (templates.length) {
    html += `<div class="mb-4"><div class="date-label">📖 Snack Recipes</div>`;
    for (const t of templates) {
      const prods = (t.products||[]).map(p => `<span class="tag">${escHtml(p.name)}${p.quantity?' ('+escHtml(p.quantity)+')':''}</span>`).join('');
      html += `<div class="meal-card">
        <span style="font-size:18px;flex-shrink:0">🍎</span>
        <div class="meal-info">
          <div class="meal-name">${escHtml(t.name)}</div>
          ${prods ? `<div class="mt-1 d-flex flex-wrap gap-1">${prods}</div>` : ''}
          ${t.notes ? `<div class="meal-notes">${escHtml(t.notes)}</div>` : ''}
        </div>
        <div class="d-flex gap-1 flex-shrink-0">
          <button class="btn btn-sm btn-mm-secondary" onclick="showSection('recipes')" title="Edit in Recipes tab">
            <i class="bi bi-pencil"></i></button>
          <button class="btn btn-sm btn-mm-secondary" onclick="addTemplateToShoppingList(${t.id})" title="Add to shopping list">
            <i class="bi bi-cart-plus"></i></button>
        </div>
      </div>`;
    }
    html += '</div>';
  }

  if (meals.length) {
    const byDate = {};
    meals.forEach(m => { (byDate[m.meal_date] = byDate[m.meal_date] || []).push(m); });
    const dates = Object.keys(byDate).sort((a,b) => b.localeCompare(a));
    for (const d of dates) {
      html += `<div class="mb-4"><div class="date-label">${fmtDate(d)}</div>`;
      for (const m of byDate[d]) {
        const prods = m.products
          ? m.products.map(p => `<span class="tag">${escHtml(p.name)}${p.quantity?' ('+escHtml(p.quantity)+')':''}</span>`).join('')
          : (m.product_count ? `<span class="tag">${m.product_count} ingredient(s)</span>` : '');
        html += `<div class="meal-card">
          <span style="font-size:18px;flex-shrink:0">🍎</span>
          <div class="meal-info">
            <div class="meal-name">${escHtml(m.name)}</div>
            ${prods ? `<div class="mt-1 d-flex flex-wrap gap-1">${prods}</div>` : ''}
            ${m.notes ? `<div class="meal-notes">${escHtml(m.notes)}</div>` : ''}
          </div>
          <div class="d-flex gap-1 flex-shrink-0">
            <button class="btn btn-sm btn-mm-secondary" onclick="addSnackToShoppingList(${m.id})" title="Add to shopping list">
              <i class="bi bi-cart-plus"></i></button>
            <button class="btn btn-sm btn-mm-danger" onclick="deleteSnack(${m.id})">
              <i class="bi bi-trash"></i></button>
          </div>
        </div>`;
      }
      html += '</div>';
    }
  }
  el.innerHTML = html;
}

function snackSearchInput(val) {
  const acList = document.getElementById('snack-ac-list');
  _snackAcIdx = -1;
  renderSnacksFiltered(val);
  const showLogged = document.getElementById('snack-show-logged').checked;
  const pool = showLogged ? [..._allSnacks, ..._allSnackTemplates] : _allSnackTemplates;
  const q = val.trim().toLowerCase();
  const seen = new Set();
  const matches = pool.filter(m => {
    const key = m.name.toLowerCase();
    if (!key.includes(q) || seen.has(key)) return false;
    seen.add(key); return true;
  });
  if (!matches.length || !q) { acList.style.display = 'none'; return; }
  acList.innerHTML = matches.map((m, i) => {
    const hi = escHtml(m.name).replace(
      new RegExp('(' + q.replace(/[.*+?^${}()|[\]\\]/g,'\\$&') + ')', 'gi'),
      '<strong>$1</strong>'
    );
    return `<div class="autocomplete-item" data-idx="${i}" onmousedown="snackAcSelect('${escHtml(m.name).replace(/'/g,"\\'")}')">
              ${hi}</div>`;
  }).join('');
  acList.style.display = 'block';
}

function snackSearchKeydown(e) {
  const acList = document.getElementById('snack-ac-list');
  const items  = acList.querySelectorAll('.autocomplete-item');
  if (!items.length) return;
  if (e.key === 'ArrowDown') { e.preventDefault(); _snackAcIdx = Math.min(_snackAcIdx+1, items.length-1); }
  else if (e.key === 'ArrowUp') { e.preventDefault(); _snackAcIdx = Math.max(_snackAcIdx-1, 0); }
  else if (e.key === 'Enter') {
    e.preventDefault();
    if (_snackAcIdx >= 0) items[_snackAcIdx].dispatchEvent(new Event('mousedown'));
    else acList.style.display = 'none'; return;
  } else if (e.key === 'Escape') { acList.style.display = 'none'; return; }
  else { return; }
  items.forEach((el, i) => el.classList.toggle('selected', i === _snackAcIdx));
}

function snackAcSelect(name) {
  document.getElementById('snack-search').value = name;
  document.getElementById('snack-ac-list').style.display = 'none';
  renderSnacksFiltered(name);
}

function clearSnackFilters() {
  document.getElementById('snack-filter-date').value = '';
  document.getElementById('snack-search').value = '';
  document.getElementById('snack-ac-list').style.display = 'none';
  loadSnacks();
}

async function addSnackToShoppingList(mealId) {
  try {
    const meal = await api('GET', `/meals/${mealId}`);
    const source = `meal:${mealId}`;
    const items = (meal.products||[]).map(p => ({ item: p.name, quantity: p.quantity||'', source }));
    if (!items.length) { toast('This snack has no ingredients.'); return; }
    const res = await api('POST', '/shopping/bulk', { items });
    toast(_shoppingAddedToast(res));
    if (res.from_fridge) loadFridge();
  } catch(e) { toast('Error: ' + e.message, true); }
}

async function addTemplateToShoppingList(tid) {
  try {
    const t = await api('GET', `/templates/${tid}`);
    const source = `template:${tid}`;
    const items = (t.products||[]).map(p => ({ item: p.name, quantity: p.quantity||'', source }));
    if (!items.length) { toast('This recipe has no ingredients.'); return; }
    const res = await api('POST', '/shopping/bulk', { items });
    toast(_shoppingAddedToast(res));
    if (res.from_fridge) loadFridge();
  } catch(e) { toast('Error: ' + e.message, true); }
}

async function deleteSnack(id) {
  if (!confirm('Delete this snack?')) return;
  try {
    await api('DELETE', `/meals/${id}`);
    toast('Snack deleted.'); loadSnacks();
  } catch(e) { toast('Error: ' + e.message, true); }
}

// ── SHOPPING LIST ─────────────────────────────────────────────────────────
async function loadShoppingList() {
  const el = document.getElementById('shop-content');
  try {
    const items = await api('GET', '/shopping/');
    if (!items.length) { el.innerHTML = '<p class="empty">Your shopping list is empty.</p>'; return; }
    el.innerHTML = items.map(it =>
      `<div class="shop-item${it.done?' done':''}" id="shop-row-${it.id}">
        <input type="checkbox" class="shop-check" ${it.done?'checked':''} onchange="toggleShopItem(${it.id})"/>
        <span class="shop-name">${escHtml(it.item)}</span>
        <span class="shop-qty">${escHtml(it.quantity)}</span>
        <button class="shop-del" onclick="deleteShopItem(${it.id})" title="Remove">✕</button>
      </div>`
    ).join('');
  } catch(e) { el.innerHTML = `<p class="empty" style="color:var(--mm-red)">${e.message}</p>`; }
}

async function addShopItem() {
  const itemEl = document.getElementById('shop-item');
  const qtyEl  = document.getElementById('shop-qty');
  const item   = itemEl.value.trim();
  if (!item) { itemEl.focus(); return; }
  try {
    await api('POST', '/shopping/', { item, quantity: qtyEl.value.trim() });
    itemEl.value = ''; qtyEl.value = ''; itemEl.focus();
    loadShoppingList();
  } catch(e) { toast('Error: ' + e.message, true); }
}

async function toggleShopItem(id) {
  try {
    const updated = await api('PUT', `/shopping/${id}/toggle`);
    const row = document.getElementById('shop-row-' + id);
    if (row) {
      row.classList.toggle('done', updated.done);
      row.querySelector('input[type=checkbox]').checked = updated.done;
    }
  } catch(e) { toast('Error: ' + e.message, true); }
}

async function deleteShopItem(id) {
  try {
    await api('DELETE', `/shopping/${id}`);
    const row = document.getElementById('shop-row-' + id);
    if (row) row.remove();
    const el = document.getElementById('shop-content');
    if (!el.querySelector('.shop-item'))
      el.innerHTML = '<p class="empty">Your shopping list is empty.</p>';
  } catch(e) { toast('Error: ' + e.message, true); }
}

async function clearDoneItems() {
  try {
    const res = await api('DELETE', '/shopping/done');
    const fridgeNote = res.added_to_fridge ? ` — ${res.added_to_fridge} restocked in the Fridge` : '';
    toast(`Cleared ${res.cleared} done item(s)${fridgeNote}.`);
    loadShoppingList();
    if (res.added_to_fridge) loadFridge();
  } catch(e) { toast('Error: ' + e.message, true); }
}

// ── FRIDGE ────────────────────────────────────────────────────────────────
let _allFridge = [];

function _fridgeQtyValue(qty) {
  const m = (qty || '').trim().match(/^(-?\d+\/\d+|-?\d+(?:[.,]\d+)?)/);
  if (!m) return null;
  const numStr = m[1];
  if (numStr.includes('/')) {
    const [n, d] = numStr.split('/');
    return parseFloat(n) / parseFloat(d);
  }
  return parseFloat(numStr.replace(',', '.'));
}

async function loadFridge() {
  const el = document.getElementById('fridge-content');
  el.innerHTML = '<p class="empty">Loading…</p>';
  try {
    _allFridge = await api('GET', '/fridge/');
    renderFridge();
  } catch(e) { el.innerHTML = `<p class="empty" style="color:var(--mm-red)">${e.message}</p>`; }
}

function renderFridge() {
  const el = document.getElementById('fridge-content');
  if (!_allFridge.length) {
    el.innerHTML = '<p class="empty">Your fridge is empty. Add what you have on hand above.</p>';
    return;
  }
  el.innerHTML = _allFridge.map(f => {
    const val = _fridgeQtyValue(f.quantity);
    const warn = (val !== null && val <= 0)
      ? `<span class="fridge-warn" title="Out of stock">⚠</span>` : '';
    return `<div class="shop-item" id="fridge-row-${f.id}">
      <span class="shop-name">${warn}${escHtml(f.name)}</span>
      <span class="shop-qty">${escHtml(f.quantity)}</span>
      <button class="btn-icon" onclick="openFridgeSendModal(${f.id})" title="Add to Shopping List"><i class="bi bi-cart-plus"></i></button>
      <button class="btn-icon" onclick="openFridgeEdit(${f.id})" title="Edit"><i class="bi bi-pencil"></i></button>
      <button class="shop-del" onclick="deleteFridgeItem(${f.id})" title="Remove">✕</button>
      <div class="wm-edit-row" id="fridge-edit-${f.id}" style="width:100%">
        <input type="text" class="form-control form-control-sm" id="fridge-edit-name-${f.id}"
               value="${escHtml(f.name)}" style="max-width:220px"
               oninput="suggestIngredientUnit(this, document.getElementById('fridge-edit-qty-${f.id}'))"/>
        <input type="text" class="form-control form-control-sm" id="fridge-edit-qty-${f.id}"
               value="${escHtml(f.quantity)}" style="max-width:140px"
               onblur="checkIngredientUnit(document.getElementById('fridge-edit-name-${f.id}'), this)"/>
        <button class="btn btn-sm btn-mm-primary" onclick="saveFridgeEdit(${f.id})"><i class="bi bi-check-lg"></i></button>
        <button class="btn btn-sm btn-mm-secondary" onclick="closeFridgeEdit(${f.id})"><i class="bi bi-x-lg"></i></button>
      </div>
    </div>`;
  }).join('');
}

function openFridgeEdit(id) {
  document.getElementById(`fridge-edit-${id}`).classList.add('visible');
}
function closeFridgeEdit(id) {
  document.getElementById(`fridge-edit-${id}`).classList.remove('visible');
}

async function saveFridgeEdit(id) {
  const name = document.getElementById(`fridge-edit-name-${id}`).value.trim();
  const qty  = document.getElementById(`fridge-edit-qty-${id}`).value.trim();
  if (!name) { toast('Please enter a name', true); return; }
  try {
    await api('PUT', `/fridge/${id}`, { name, quantity: qty });
    toast('✔ Updated!');
    loadFridge();
  } catch(e) { toast(e.message, true); }
}

async function deleteFridgeItem(id) {
  if (!confirm('Remove this item from the fridge?')) return;
  try {
    await api('DELETE', `/fridge/${id}`);
    toast('Removed.');
    loadFridge();
  } catch(e) { toast(e.message, true); }
}

async function addFridgeBulk() {
  const ta = document.getElementById('fridge-bulk-input');
  const lines = ta.value.split('\n').map(l => l.trim()).filter(Boolean);
  const items = lines.map(line => {
    const idx = line.indexOf('-');
    if (idx === -1) return { name: line, quantity: '' };
    return { name: line.slice(0, idx).trim(), quantity: line.slice(idx + 1).trim() };
  }).filter(it => it.name);
  if (!items.length) { toast('Type at least one item, e.g. "Яйце - 10 бр"', true); return; }
  try {
    const res = await api('POST', '/fridge/bulk', { items });
    toast(`✔ Added ${res.added} item(s) to the Fridge.`);
    ta.value = '';
    loadFridge();
  } catch(e) { toast(e.message, true); }
}

let _fridgeSendName = null;

function openFridgeSendModal(id) {
  const item = _allFridge.find(f => f.id === id);
  if (!item) return;
  _fridgeSendName = item.name;
  document.getElementById('fridge-send-title').textContent = `Add "${item.name}" to Shopping List`;
  document.getElementById('fridge-send-qty').value = '';
  document.getElementById('fridge-send-overlay').classList.add('show');
  document.getElementById('fridge-send-qty').focus();
}

function closeFridgeSendModal() {
  document.getElementById('fridge-send-overlay').classList.remove('show');
  _fridgeSendName = null;
}

async function sendFridgeToShoppingList() {
  const qty = document.getElementById('fridge-send-qty').value.trim();
  if (!_fridgeSendName || !qty) { toast('Please enter a quantity', true); return; }
  try {
    await api('POST', '/shopping/', { item: _fridgeSendName, quantity: qty });
    toast(`✔ Added "${_fridgeSendName}" to the Shopping List.`);
    closeFridgeSendModal();
    loadShoppingList();
  } catch(e) { toast('Error: ' + e.message, true); }
}

// ── SEND RECOMMENDATION → WEEKLY MENU ────────────────────────────────────
async function sendRecToWeeklyMenu() {
  if (!_lastRecData) return;
  try {
    if (_lastRecData.mode === 'week') {
      // Full week: use bulk from-rec endpoint
      const weekStart = _lastRecData.data.start_date;
      await api('POST', '/weekly-menu/from-rec', {
        week_start: weekStart,
        days: _lastRecData.data.days,
      });
      _wmWeekStart = weekStart;
    } else {
      // Single day: compute correct Monday + day_offset, then set each slot
      const rec        = _lastRecData.data;
      const targetDate = rec.target_date;
      const monday     = _wmMonday(targetDate);
      // day_offset: how many days from Monday to targetDate
      const msPerDay   = 86400000;
      const monMs      = new Date(monday + 'T00:00:00').getTime();
      const tgtMs      = new Date(targetDate + 'T00:00:00').getTime();
      const dayOffset  = Math.round((tgtMs - monMs) / msPerDay);

      const slots = ['breakfast', 'lunch', 'dinner'];
      for (const slot of slots) {
        const r = rec[slot];
        if (!r || r.meal_name === 'No recipes found') continue;
        const products = (r.suggested_products || []).map(p =>
          typeof p === 'object' ? { name: p.name, quantity: p.quantity || '' } : { name: p, quantity: '' }
        );
        await api('PUT', '/weekly-menu/slot', {
          week_start: monday,
          day_offset: dayOffset,
          slot,
          meal_name: r.meal_name,
          products,
        });
      }
      _wmWeekStart = monday;
    }
    toast('✔ Sent to Weekly Menu!');
    showSection('weeklymenu');
  } catch(e) { toast('Error: ' + e.message, true); }
}

// ── WEEKLY MENU ───────────────────────────────────────────────────────────
let _wmWeekStart = null;   // ISO date string (Monday)

// Use local-date arithmetic to avoid UTC timezone shift bugs.
function _localIso(d) {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}

function _wmMonday(isoDate) {
  const d = new Date(isoDate + 'T00:00:00');
  const dow = d.getDay();                    // 0=Sun … 6=Sat
  const diff = (dow === 0) ? -6 : 1 - dow;  // shift to Monday
  d.setDate(d.getDate() + diff);
  return _localIso(d);
}

function _wmAddDays(isoDate, n) {
  const d = new Date(isoDate + 'T00:00:00');
  d.setDate(d.getDate() + n);
  return _localIso(d);
}

function wmPrevWeek() {
  if (!_wmWeekStart) return;
  _wmWeekStart = _wmAddDays(_wmWeekStart, -7);
  loadWeeklyMenu();
}
function wmNextWeek() {
  if (!_wmWeekStart) return;
  _wmWeekStart = _wmAddDays(_wmWeekStart, 7);
  loadWeeklyMenu();
}

async function loadWeeklyMenu() {
  if (!_wmWeekStart) {
    // Default: current week's Monday
    _wmWeekStart = _wmMonday(_localIso(new Date()));
  }
  const el = document.getElementById('wm-content');
  el.innerHTML = '<p class="empty">Loading…</p>';
  try {
    const data = await api('GET', `/weekly-menu/?week_start=${_wmWeekStart}`);
    _wmWeekStart = data.week_start;
    const endDate = _wmAddDays(_wmWeekStart, 6);
    document.getElementById('wm-week-label').textContent =
      `${_wmWeekStart}  →  ${endDate}`;
    renderWeeklyMenu(data.slots);
  } catch(e) { el.innerHTML = `<p class="empty" style="color:var(--mm-red)">${e.message}</p>`; }
}

async function wmClearWeek() {
  if (!_wmWeekStart) return;
  if (!confirm('Clear all meals for this week?')) return;
  try {
    await api('DELETE', `/weekly-menu/clear?week_start=${_wmWeekStart}`);
    toast('Week cleared.');
    loadWeeklyMenu();
  } catch(e) { toast('Error: ' + e.message, true); }
}

function renderWeeklyMenu(slots) {
  const el = document.getElementById('wm-content');
  // Group by day_offset
  const days = {};
  slots.forEach(s => {
    if (!days[s.day_offset]) days[s.day_offset] = { name: s.day_name, offset: s.day_offset, slots: {} };
    days[s.day_offset].slots[s.slot] = s;
  });

  const slotColors = { breakfast: 'var(--mm-yellow)', lunch: 'var(--mm-green)', dinner: 'var(--mm-accent)' };
  let html = '';
  for (let i = 0; i < 7; i++) {
    const day = days[i];
    if (!day) continue;
    const dayDate = _wmAddDays(_wmWeekStart, i);
    html += `<div class="wm-day-card">
      <div class="wm-day-header">
        <div>
          <span class="wm-day-name">${day.name}</span>
          <span class="wm-day-date ms-2">${dayDate}</span>
        </div>
        <button class="btn btn-sm btn-mm-secondary" onclick="wmExportDay(${i})" title="Export day ingredients to Shopping List">
          <i class="bi bi-cart-plus me-1"></i>Add to Shopping List</button>
      </div>
      <div class="wm-slots">`;

    for (const slot of ['breakfast', 'lunch', 'dinner']) {
      const s = day.slots[slot] || {};
      const name = s.meal_name || '';
      const products = s.products || [];
      const slotId = `wm-${i}-${slot}`;
      const tags = products.map(p => {
        const label = p.quantity ? `${p.name} (${p.quantity})` : p.name;
        return `<span class="tag">${escHtml(label)}</span>`;
      }).join('');

      html += `<div class="wm-slot-row" id="${slotId}-row">
        <span class="wm-slot-label" style="color:${slotColors[slot]}">${slot}</span>
        <span class="wm-slot-name${name ? ' wm-slot-name-clickable' : ' empty-slot'}" id="${slotId}-name"
          ${name ? `onclick="showMealDetail(this.textContent.trim())" title="Click for recipe details"` : ''}>
          ${name ? escHtml(name) : 'Not set'}</span>
        <div class="wm-slot-products" id="${slotId}-products">${tags}</div>
        ${name ? `<button class="btn btn-sm btn-mm-secondary ms-auto" onclick="markSlotCooked(${i}, '${slot}', '${dayDate}')" title="Mark as cooked">
          <i class="bi bi-check2-circle"></i></button>` : '<span class="ms-auto"></span>'}
        <button class="btn btn-sm btn-mm-secondary" onclick="wmOpenEdit('${slotId}', ${i}, '${slot}')">
          <i class="bi bi-pencil"></i></button>
      </div>
      <div class="wm-edit-row" id="${slotId}-edit">
        <div class="autocomplete-wrap" style="flex:1;min-width:160px">
          <input id="${slotId}-input" class="form-control form-control-sm" type="text"
                 placeholder="Meal name…" value="${escHtml(name)}"
                 autocomplete="off"
                 oninput="wmAcInput(this, '${slotId}')"
                 onkeydown="wmAcKeydown(event, '${slotId}', ${i}, '${slot}')"
                 onfocus="wmAcInput(this, '${slotId}')"/>
          <div id="${slotId}-ac" class="autocomplete-list" style="display:none"></div>
        </div>
        <button class="btn btn-sm btn-mm-primary"   onclick="wmSaveSlot('${slotId}', ${i}, '${slot}')">
          <i class="bi bi-check-lg"></i></button>
        <button class="btn btn-sm btn-mm-secondary" onclick="wmCloseEdit('${slotId}')">
          <i class="bi bi-x-lg"></i></button>
      </div>`;
    }
    html += `</div></div>`;
  }
  el.innerHTML = html;
}

// ── meal detail modal (click a meal name in Weekly Menu) ──────────────────
async function showMealDetail(name) {
  if (!name) return;
  await _loadAcMeals();
  const m = _acMeals.find(x => x.name.toLowerCase() === name.toLowerCase());
  const overlay = document.getElementById('meal-detail-overlay');
  const body    = document.getElementById('meal-detail-body');
  if (!m) {
    body.innerHTML = `<div class="meal-detail-title">${escHtml(name)}</div>
      <p class="no-recipe">No saved recipe or logged details found for this meal.</p>`;
    overlay.classList.add('show');
    return;
  }
  const badgeColors = {breakfast:'background:#3d2e0a;color:#fbbf24', lunch:'background:#0d2e1a;color:#34d399', dinner:'background:#0d1a3d;color:#6c8ef5', snack:'background:#2a1a3d;color:#c084fc'};
  const types  = (m.meal_types && m.meal_types.length) ? m.meal_types : [m.meal_type];
  const badges = types.map(t =>
    `<span class="meal-type-badge" style="${badgeColors[t]};font-size:10px;padding:2px 8px;border-radius:4px;font-weight:700;text-transform:uppercase;margin-right:3px">${t}</span>`
  ).join('') + ((typeof m.calories === 'number') ? `<span class="tag" style="margin-left:2px">🔥 ${m.calories.toLocaleString()} kcal</span>` : '');
  const ingredients = (m.products && m.products.length)
    ? `<div class="recipe-section-title">Ingredients</div>
       <div class="ingredient-list">${m.products.map(p => `<div class="ingredient-row"><span>${escHtml(p.name)}</span><span class="ingredient-qty">${escHtml(p.quantity||'—')}</span></div>`).join('')}</div>`
    : `<div class="recipe-section-title">Ingredients</div><p class="no-recipe">No ingredients listed.</p>`;
  const recipeBlock = m.recipe
    ? `<div class="recipe-section-title">Recipe</div><div class="recipe-text">${escHtml(m.recipe)}</div>`
    : `<div class="recipe-section-title">Recipe</div><p class="no-recipe">No recipe added yet.</p>`;
  const methodsBlock = (m.methods && m.methods.length)
    ? `<div class="recipe-section-title">Cooking Method</div>
       <div class="mb-2">${m.methods.map(mm => `<span class="tag" style="margin-right:4px">${METHOD_LABELS[mm]||mm}</span>`).join('')}</div>`
    : '';
  const notesBlock = m.notes
    ? `<div class="recipe-section-title">Notes</div><p style="font-size:13px;color:var(--mm-accent2);font-style:italic">${escHtml(m.notes)}</p>`
    : '';
  body.innerHTML = `<div class="meal-detail-title">${escHtml(m.name)}</div>
    <div class="mb-2">${badges}</div>
    ${ingredients}${recipeBlock}${methodsBlock}${notesBlock}`;
  overlay.classList.add('show');
}

function closeMealDetail() {
  document.getElementById('meal-detail-overlay').classList.remove('show');
}

// ── weekly menu inline edit ───────────────────────────────────────────────
let _wmAcIdx = {};   // per-slotId keyboard index

function wmOpenEdit(slotId, dayOffset, slot) {
  document.getElementById(slotId + '-edit').classList.add('visible');
  document.getElementById(slotId + '-input').focus();
}
function wmCloseEdit(slotId) {
  document.getElementById(slotId + '-edit').classList.remove('visible');
  const ac = document.getElementById(slotId + '-ac');
  if (ac) ac.style.display = 'none';
}

// Logs the slot's meal (same as Add Meal) and settles the Fridge — consuming
// only whatever was bought specifically for this slot's shortfall, since
// anything the Fridge already had was already taken out when this slot was
// exported to the Shopping List.
async function markSlotCooked(dayOffset, slot, mealDate) {
  const slotId = `wm-${dayOffset}-${slot}`;
  const nameEl = document.getElementById(`${slotId}-name`);
  const name = nameEl ? nameEl.textContent.trim() : '';
  if (!name) return;
  if (!confirm(`Mark "${name}" as cooked? This logs it to your Meal Log and updates your Fridge.`)) return;

  await _loadAcMeals();
  const match = _acMeals.find(m => m.name.toLowerCase() === name.toLowerCase());

  let products, recipe, notes, calories;
  if (match) {
    products = match.products || [];
    recipe   = match.recipe || '';
    notes    = match.notes || '';
    calories = (typeof match.calories === 'number') ? match.calories : null;
  } else {
    products = [];
    const tagsEl = document.getElementById(`${slotId}-products`);
    if (tagsEl) {
      tagsEl.querySelectorAll('.tag').forEach(tag => {
        const text = tag.textContent.trim();
        const m = text.match(/^(.+?)\s*\(([^)]+)\)$/);
        products.push(m ? { name: m[1].trim(), quantity: m[2].trim() } : { name: text, quantity: '' });
      });
    }
    recipe = ''; notes = ''; calories = null;
  }

  const source = `wm:${_wmWeekStart}:${dayOffset}:${slot}`;
  try {
    const res = await api('POST', '/fridge/cooked', {
      source,
      meal: { name, meal_type: slot, meal_date: mealDate, notes, recipe, calories, products },
    });
    toast(`✔ Logged "${name}"${res.fridge_settled ? ' and updated the Fridge' : ''}.`);
    if (res.fridge_settled) loadFridge();
    loadLog();
  } catch(e) { toast('Error: ' + e.message, true); }
}

async function wmSaveSlot(slotId, dayOffset, slot) {
  const input = document.getElementById(slotId + '-input');
  const mealName = input.value.trim();

  // Look up products from templates/meals cache
  let products = [];
  const match = _acMeals.find(m => m.name.toLowerCase() === mealName.toLowerCase());
  if (match && match.products) {
    products = match.products.map(p => ({ name: p.name, quantity: p.quantity || '' }));
  }

  try {
    const updated = await api('PUT', '/weekly-menu/slot', {
      week_start: _wmWeekStart, day_offset: dayOffset, slot,
      meal_name: mealName, products,
    });
    // Patch view in-place
    const nameEl = document.getElementById(slotId + '-name');
    nameEl.textContent = mealName || 'Not set';
    nameEl.classList.toggle('empty-slot', !mealName);
    nameEl.classList.toggle('wm-slot-name-clickable', !!mealName);
    nameEl.onclick = mealName ? () => showMealDetail(mealName) : null;
    nameEl.title = mealName ? 'Click for recipe details' : '';
    const tags = (updated.products || []).map(p => {
      const label = p.quantity ? `${p.name} (${p.quantity})` : p.name;
      return `<span class="tag">${escHtml(label)}</span>`;
    }).join('');
    document.getElementById(slotId + '-products').innerHTML = tags;
    wmCloseEdit(slotId);
    toast('✔ Saved!');
  } catch(e) { toast('Error: ' + e.message, true); }
}

function wmAcInput(inputEl, slotId) {
  _loadAcMeals();
  const q = inputEl.value.trim().toLowerCase();
  const acList = document.getElementById(slotId + '-ac');
  _wmAcIdx[slotId] = -1;
  const matches = q ? _acMeals.filter(m => m.name.toLowerCase().includes(q)) : _acMeals;
  if (!matches.length) { acList.style.display = 'none'; return; }
  const badgeColors = {breakfast:'background:#3d2e0a;color:#fbbf24', lunch:'background:#0d2e1a;color:#34d399', dinner:'background:#0d1a3d;color:#6c8ef5', snack:'background:#2a1a3d;color:#c084fc'};
  acList.innerHTML = matches.slice(0, 20).map((m, i) =>
    `<div class="autocomplete-item" data-idx="${i}"
          onmousedown="wmAcSelect('${slotId}', '${escHtml(m.name).replace(/'/g,"\\'")}')">
       <span class="ac-badge" style="${badgeColors[m.meal_type]}">${m.meal_type}</span>${escHtml(m.name)}
     </div>`
  ).join('');
  acList._matches = matches;
  acList.style.display = 'block';
}

function wmAcSelect(slotId, name) {
  document.getElementById(slotId + '-input').value = name;
  document.getElementById(slotId + '-ac').style.display = 'none';
  _wmAcIdx[slotId] = -1;
}

function wmAcKeydown(e, slotId, dayOffset, slot) {
  const acList = document.getElementById(slotId + '-ac');
  const items  = acList.querySelectorAll('.autocomplete-item');
  if (e.key === 'Enter') {
    e.preventDefault();
    if (_wmAcIdx[slotId] >= 0 && items[_wmAcIdx[slotId]]) {
      items[_wmAcIdx[slotId]].dispatchEvent(new Event('mousedown'));
    }
    wmSaveSlot(slotId, dayOffset, slot);
    return;
  }
  if (!items.length) return;
  if (e.key === 'ArrowDown') { e.preventDefault(); _wmAcIdx[slotId] = Math.min((_wmAcIdx[slotId]||0)+1, items.length-1); }
  else if (e.key === 'ArrowUp') { e.preventDefault(); _wmAcIdx[slotId] = Math.max((_wmAcIdx[slotId]||0)-1, 0); }
  else if (e.key === 'Escape') { acList.style.display = 'none'; return; }
  else { return; }
  items.forEach((el, i) => el.classList.toggle('selected', i === _wmAcIdx[slotId]));
  if (items[_wmAcIdx[slotId]]) items[_wmAcIdx[slotId]].scrollIntoView({block:'nearest'});
}

async function wmExportDay(dayOffset) {
  const el = document.getElementById('wm-content');
  // Collect all products for this day from the rendered slots
  const items = [];
  for (const slot of ['breakfast', 'lunch', 'dinner']) {
    const slotId = `wm-${dayOffset}-${slot}`;
    const nameEl = document.getElementById(slotId + '-name');
    if (!nameEl || nameEl.classList.contains('empty-slot')) continue;
    // Get products from the tag spans
    const prodEl = document.getElementById(slotId + '-products');
    if (prodEl) {
      const source = `wm:${_wmWeekStart}:${dayOffset}:${slot}`;
      prodEl.querySelectorAll('.tag').forEach(tag => {
        const text = tag.textContent.trim();
        // Parse "name (qty)" or just "name"
        const m = text.match(/^(.+?)\s*\(([^)]+)\)$/);
        items.push(m ? { item: m[1].trim(), quantity: m[2].trim(), source } : { item: text, quantity: '', source });
      });
    }
  }
  if (!items.length) { toast('No ingredients to export for this day.'); return; }
  try {
    const res = await api('POST', '/shopping/bulk', { items });
    toast(_shoppingAddedToast(res));
    if (res.from_fridge) loadFridge();
  } catch(e) { toast('Error: ' + e.message, true); }
}

// ── textarea auto-grow ─────────────────────────────────────────────────────
function autoGrow(el) {
  el.style.height = 'auto';
  el.style.height = el.scrollHeight + 'px';
}
window.addEventListener('resize', () => {
  const el = document.getElementById('f-recipe');
  if (el && el.value) autoGrow(el);
});

// ── init ──────────────────────────────────────────────────────────────────
addProductRow();
_checkSession();
</script>
<!-- Bootstrap 5 JS bundle (includes Popper) -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

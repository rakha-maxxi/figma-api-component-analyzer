"""Demo Figma-like payload for local verification without API access."""

from copy import deepcopy


def build_demo_file():
    summary_card = _component(
        "201:1",
        "Summary Card",
        width=312,
        height=148,
        children=[
            _text("201:2", "Title"),
            _text("201:3", "Subtitle"),
            _frame(
                "201:4",
                "Metrics",
                layout="HORIZONTAL",
                width=280,
                height=54,
                children=[
                    _metric_pair("201:5", "Omzet", "Rp70.000.000"),
                    _metric_pair("201:8", "Retailer Scan", "28 / 123"),
                ],
            ),
        ],
    )

    section_overview = _component(
        "202:1",
        "Sales Overview Section",
        width=360,
        height=420,
        children=[
            _frame(
                "202:2",
                "Header",
                layout="HORIZONTAL",
                width=328,
                height=48,
                children=[
                    _text("202:3", "Target Penjualan"),
                    _button("202:4", "Lihat Semua"),
                ],
            ),
            _instance("202:5", "Summary Card / 1", "201:1", width=312, height=148),
            _instance("202:6", "Summary Card / 2", "201:1", width=312, height=148),
            _frame(
                "202:7",
                "Footer CTA",
                layout="HORIZONTAL",
                width=320,
                height=44,
                children=[_button("202:8", "Tinjau Detail"), _button("202:9", "Bandingkan")],
            ),
        ],
    )

    promo_section = _frame(
        "301:1",
        "Promo Summary Section",
        width=328,
        height=220,
        layout="VERTICAL",
        children=[
            _section_header("301:2", "Promo minggu ini"),
            _native_summary_card("301:3", "Retailer A", "Rp18.000.000", "6 brand"),
            _native_summary_card("301:10", "Retailer B", "Rp12.000.000", "4 brand"),
        ],
    )

    product_rows = [
        _product_row(f"401:{index}", f"Produk {index}", "Herbisida", f"Rp{index}.500.000", "120 Ton")
        for index in range(1, 5)
    ]
    product_list = _frame(
        "401:100",
        "Top Product List",
        width=328,
        height=280,
        layout="VERTICAL",
        children=[_section_header("401:101", "Top Scan Produk"), *product_rows],
    )

    screen_home = _frame(
        "100:1",
        "Home / Dashboard",
        width=390,
        height=844,
        children=[
            _frame(
                "100:2",
                "Hero Header",
                width=390,
                height=156,
                children=[_text("100:3", "Toko Tani Jaya"), _text("100:4", "Ngancar, Kab. Kediri")],
            ),
            _instance("100:5", "Sales Overview", "202:1", width=360, height=420),
            promo_section,
            product_list,
        ],
    )

    screen_compare = _frame(
        "100:10",
        "Compare / Dashboard",
        width=390,
        height=844,
        children=[
            _frame(
                "100:11",
                "Compare Header",
                width=390,
                height=64,
                children=[_chip("100:12", "Filter"), _chip("100:13", "Bandingkan")],
            ),
            _native_summary_card("100:14", "Retailer C", "Rp15.000.000", "8 brand"),
            _native_summary_card("100:21", "Retailer D", "Rp11.500.000", "5 brand"),
            _instance("100:23", "Noteview / From Master", "901:1", width=312, height=92),
            _noteview_native("100:24", "Catatan approval belum diisi"),
            _product_row("100:28", "MAXXFOSATE NEO", "Herbisida", "Rp5.200.000", "120 Ton"),
            _product_row("100:35", "HARBER 60 WP", "Herbisida", "Rp8.640.000", "120 Ton"),
            _noteview_native("100:42", "Mohon revisi nominal diskon"),
        ],
    )

    return {
        "name": "Demo MAI File",
        "document": {
            "id": "0:0",
            "name": "Document",
            "type": "DOCUMENT",
            "children": [
                {
                    "id": "1:1",
                    "name": "FS+ Page",
                    "type": "CANVAS",
                    "children": [screen_home, screen_compare, summary_card, section_overview],
                }
            ],
        },
        "components": {
            "201:1": {"key": "local-summary-card", "name": "Summary Card"},
            "202:1": {"key": "local-sales-overview-section", "name": "Sales Overview Section"},
            "901:1": {"key": "master-noteview", "name": "Noteview", "remote": True, "file_key": "demo-master"},
        },
    }


def build_demo_master_file():
    noteview = _component(
        "901:1",
        "Noteview",
        width=312,
        height=92,
        children=[
            _text("901:2", "Title"),
            _frame(
                "901:3",
                "Content",
                width=280,
                height=36,
                children=[_text("901:4", "Isi catatan untuk approval dan revisi")],
            ),
        ],
    )

    section_shell = _component(
        "902:1",
        "Section Shell",
        width=328,
        height=180,
        children=[
            _section_header("902:2", "Section Title"),
            _frame("902:3", "Content Slot", width=296, height=84, children=[_text("902:4", "Slot")]),
        ],
    )

    return {
        "name": "Demo MAI Master",
        "document": {
            "id": "0:0",
            "name": "Document",
            "type": "DOCUMENT",
            "children": [
                {
                    "id": "1:1",
                    "name": "MM+ Master",
                    "type": "CANVAS",
                    "children": [noteview, section_shell],
                }
            ],
        },
        "components": {
            "901:1": {"key": "master-noteview", "name": "Noteview"},
            "902:1": {"key": "master-section-shell", "name": "Section Shell"},
        },
    }


def _component(node_id, name, width, height, children):
    node = _frame(node_id, name, width=width, height=height, children=children)
    node["type"] = "COMPONENT"
    return node


def _instance(node_id, name, component_id, width, height):
    return {
        "id": node_id,
        "name": name,
        "type": "INSTANCE",
        "componentId": component_id,
        "absoluteBoundingBox": {"width": width, "height": height},
    }


def _frame(node_id, name, width, height, children=None, layout="VERTICAL"):
    return {
        "id": node_id,
        "name": name,
        "type": "FRAME",
        "layoutMode": layout,
        "itemSpacing": 12,
        "paddingLeft": 16,
        "paddingRight": 16,
        "paddingTop": 16,
        "paddingBottom": 16,
        "absoluteBoundingBox": {"width": width, "height": height},
        "children": deepcopy(children or []),
    }


def _text(node_id, name):
    return {"id": node_id, "name": name, "type": "TEXT"}


def _button(node_id, name):
    return _frame(node_id, name, width=104, height=40, children=[_text(f"{node_id}:label", name)], layout="HORIZONTAL")


def _chip(node_id, name):
    return _frame(node_id, name, width=88, height=32, children=[_text(f"{node_id}:label", name)], layout="HORIZONTAL")


def _metric_pair(base_id, label, value):
    return _frame(
        base_id,
        f"{label} Pair",
        width=132,
        height=54,
        children=[_text(f"{base_id}:1", label), _text(f"{base_id}:2", value)],
    )


def _section_header(node_id, title):
    return _frame(
        node_id,
        "Section Header",
        width=296,
        height=44,
        layout="HORIZONTAL",
        children=[_text(f"{node_id}:1", title), _button(f"{node_id}:2", "Lihat Semua")],
    )


def _native_summary_card(node_id, title, omzet, meta):
    return _frame(
        node_id,
        "Native Summary Card",
        width=312,
        height=148,
        children=[
            _text(f"{node_id}:1", title),
            _text(f"{node_id}:2", "Ngancar, Kab. Kediri"),
            _frame(
                f"{node_id}:3",
                "Metrics",
                width=280,
                height=54,
                layout="HORIZONTAL",
                children=[_metric_pair(f"{node_id}:4", "Omzet", omzet), _metric_pair(f"{node_id}:7", "Brand Aktif", meta)],
            ),
        ],
    )


def _product_row(node_id, title, subtitle, value, volume):
    return _frame(
        node_id,
        "Product Summary Row",
        width=312,
        height=88,
        layout="HORIZONTAL",
        children=[
            _text(f"{node_id}:1", title),
            _text(f"{node_id}:2", subtitle),
            _metric_pair(f"{node_id}:3", "Omzet", value),
            _metric_pair(f"{node_id}:6", "Jumlah Scan", volume),
            _text(f"{node_id}:9", "Chevron"),
        ],
    )


def _noteview_native(node_id, message):
    return _frame(
        node_id,
        "Noteview",
        width=312,
        height=92,
        children=[
            _text(f"{node_id}:1", "Title"),
            _frame(
                f"{node_id}:2",
                "Content",
                width=280,
                height=36,
                children=[_text(f"{node_id}:3", message)],
            ),
        ],
    )

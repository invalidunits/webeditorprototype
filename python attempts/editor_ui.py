from nicegui import ui

# ==========================================
# 1. STATE
# ==========================================
doc_state = {
    'title': 'Untitled Document',
    'content': ''
}


# ==========================================
# 2. LOGIC
# ==========================================
def clear_input():
    doc_state['content'] = ''


def save():
    print(f"--- SAVING ---")
    print(f"Title: {doc_state['title']}")
    print(f"Content:\n{doc_state['content']}\n")


# ==========================================
# 3. LAYOUT
# ==========================================

ui.query('.nicegui-content').classes('p-0')

# --- The Header ---
# 'bg-white' makes it white, 'border-b' adds a subtle line at the bottom
# We removed 'justify-between' so everything naturally packs to the left
with ui.header().classes('bg-white border-b border-gray-200 py-2 px-4 items-center flex-row gap-6'):
    # 1. Editable Title (Now on the far left)
    # Removed the 'dark' prop so the text renders clearly on the white background
    ui.input() \
        .bind_value(doc_state, 'title') \
        .props('dense input-class="text-2xl font-bold text-gray-800"') \
        .classes('w-64')  # Gives the title a fixed width so it doesn't push the buttons away

    # 2. Buttons (To the right of the title)
    with ui.row().classes('gap-1'):
        # .props('flat size=sm') makes them small, text-only buttons
        ui.button('Save', on_click=save, color='blue').props('flat size=sm')
        ui.button('Clear', on_click=clear_input, color='red').props('flat size=sm')


# --- The Body ("The Desk") ---
with ui.column().classes('w-full min-h-screen items-center bg-gray-100 py-8'):
    # --- The Text Box ("The Paper") ---
    text_box = ui.textarea('') \
        .bind_value(doc_state, 'content') \
        .props('borderless autocomplete=nope autocorrect=off spellcheck=false autogrow') \
        .classes('w-full max-w-4xl bg-white text-lg p-10 min-h-[100vh] shadow-md')

ui.run()
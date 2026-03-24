# editor_ui.py
from nicegui.functions.navigate import navigate

import file_manager as b
from nicegui import ui


# Landing Screen
@ui.page('/')
def landing_page():
    def handle_create():
        b.create_file()
        ui.navigate.to('/')
    #it had a weird white border so thats why this is here
    ui.query('.nicegui-content').classes('p-0')

    with ui.column().classes('w-full min-h-screen items-center py-12 bg-gray-100'):
        ui.label('Select a Document').classes('text-3xl font-bold text-gray-800 mb-6')

        available_files = b.get_files()

        # Added 'px-4' here so the cards don't scrape the absolute edge of a small browser window
        with ui.column().classes('gap-3 w-full max-w-3xl px-4'):

            # 2. FIXED THE BUTTON
            # Using props('outline color=green') guarantees the Quasar button formats the text correctly
            ui.button('+ Create New Document', on_click=handle_create) \
                .props('outline color=green') \
                .classes('w-full mb-4 bg-white text-lg font-bold shadow-sm')

            if not available_files:
                ui.label("No files found.").classes('text-gray-500 italic text-center w-full py-8')

            for filename in available_files:
                last_edited = b.get_time_ago(filename)

                with ui.card().classes(
                        'w-full p-4 flex-row justify-between items-center cursor-pointer hover:bg-gray-200 transition-colors shadow-sm') \
                        .on('click', lambda f=filename: ui.navigate.to(f'/editor/{f}')):
                    ui.label(filename).classes('text-lg font-semibold text-gray-800')
                    ui.label(f'Last edited {last_edited}').classes('text-sm text-gray-500 font-medium')


@ui.page('/editor/{filename}')
def render_editor(filename: str):
    # 1. STATE
    doc_state = b.read_file(filename)


    # 2. LOGIC

    def delete():
        b.del_file(doc_state['title'])
        ui.navigate.history.replace(f'/')
        ui.navigate.to('/')

    def save():
        # You will hook this up to your .md saving logic later!
        print(f"--- SAVING {doc_state['title']}---")
        b.save_file(doc_state['oldTitle'],doc_state["title"], doc_state['content'])
        ui.navigate.history.replace(f'/editor/{doc_state['title']}')



    # 3. LAYOUT

    ui.query('.nicegui-content').classes('p-0')

    # header
    with ui.header().classes('bg-white border-b border-gray-200 py-2 px-4 items-center flex-row gap-6'):

        #home button
        ui.button(on_click=lambda: ui.navigate.to('/')) \
            .classes('w-10 h-10 bg-[#F5F5DC]') \
            .props('square unelevated')
        #title field
        ui.input() \
            .bind_value(doc_state, 'title') \
            .props('dense input-class="text-2xl font-bold text-gray-800"') \
            .classes('w-64')
        #save and delete buttons
        with ui.row().classes('gap-1'):
            ui.button('Save', on_click=save, color='blue').props('flat size=sm')
            ui.button('Delete', on_click=delete, color='red').props('flat size=sm')

    # body
    with ui.column().classes('w-full min-h-screen items-center bg-gray-100 py-8'):
        text_box = ui.textarea('') \
            .bind_value(doc_state, 'content') \
            .props('borderless autocomplete=nope autocorrect=off spellcheck=false autogrow') \
            .classes('w-full max-w-4xl bg-white text-lg px-10 py-1 min-h-[100vh] shadow-md')
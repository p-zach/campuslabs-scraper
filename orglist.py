import tkinter as tk
import requests
import json

class OrganizationList(tk.Frame):
    def __init__(self, root, links, *args, **kwargs):
        tk.Frame.__init__(self, root, *args, **kwargs)
        self.root = root

        self.vsb = tk.Scrollbar(self, orient="vertical")
        self.text = tk.Text(self, width=40, height=20, 
                            yscrollcommand=self.vsb.set)
        self.vsb.config(command=self.text.yview)
        self.vsb.pack(side="right", fill="y")
        self.text.pack(side="left", fill="both", expand=True)

        for name, contact in self.get_links_info(links):
            cb = tk.Checkbutton(self, text=f"{name}: {contact}")
            self.text.window_create("end", window=cb)
            self.text.insert("end", "\n") # to force one checkbox per line

    def get_links_info(self, links):
        for link in links:
            page = requests.get(link)
            org_details = self.get_org_details(str(page.content))
            data = org_details['preFetchedData']['organization']
            name = data['name']
            contact = None
            try:
                contact = data['email'] if data['email'] else f"{data['primaryContact']['primaryEmailAddress']} (primary contact)"
            except KeyError: pass
            if contact is None:
                contact = link + "/contact"

            yield name, contact

    def get_org_details(self, html_text):
        page_desc_begin = "window.initialAppState = "
        page_desc_end = ";</script>"
        new_text = html_text[html_text.find(page_desc_begin) + len(page_desc_begin):]
        new_text = new_text[:new_text.find(page_desc_end)]
        new_text = new_text.replace(r'\\"', '')
        new_text = new_text.replace('\\', '')
        return json.loads(new_text)
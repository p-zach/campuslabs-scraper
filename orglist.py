import tkinter as tk
import requests
import json
import asyncio

class OrganizationList(tk.Frame):
    """Shows a list of CampusLabs organizations and provides checkboxes for the user
    to specify whether they want to include the organization in the output data.
    """
    def __init__(self, root, links, *args, **kwargs):
        tk.Frame.__init__(self, root, *args, **kwargs)
        self.root = root

        # create window layout
        self.vsb = tk.Scrollbar(self, orient="vertical")
        self.text = tk.Text(self, width=70, height=40, 
                            yscrollcommand=self.vsb.set)
        self.vsb.config(command=self.text.yview)
        self.vsb.pack(side="right", fill="y")
        self.text.pack(side="left", fill="both", expand=True)

        self.loop = asyncio.get_event_loop()

        self.values = {}

        # get name and contact for each organization
        for name, contact in self.get_links_info(links):
            # create checkboxes for the organizations
            val = tk.BooleanVar()
            cb = tk.Checkbutton(self, text=f"{name}: {contact}", variable=val)
            self.values[name] = (val, contact)
            self.text.window_create("end", window=cb)
            self.text.insert("end", "\n") # to force one checkbox per line

        button = tk.Button(self, text="Export", command=self.export_selected_orgs)
        button.pack(side=tk.BOTTOM)
    
    def export_selected_orgs(self):
        self.text.delete(1.0, tk.END)
        for org, details in self.values.items():
            if details[0].get():
                self.text.insert(tk.END, f"{org},{details[1]}\n")

    def get_links_info(self, links):
        """Get the name and contact information for the CampusLabs organizations linked to by the provided list.

        Args:
            links (list): the list of URLs to the organizations.

        Yields:
            tuple: (name of organization, contact info for organization)
        """
        # process organization details as they are retrieved from online
        for org_details in asyncio.as_completed([self.get_org_details(link) for link in links]):
            # wonky async clarification
            data, link = self.loop.run_until_complete(org_details)
            # get only the part of the json we care about
            data = data['preFetchedData']['organization']
            # get the organization name
            name = data['name']
            # get the either the organization email, the primary contact email, or the contact page link
            contact = None
            try:
                contact = data['email'] if data['email'] else f"{data['primaryContact']['primaryEmailAddress']}"
            except KeyError: pass
            except TypeError: pass
            if contact is None:
                contact = link + "/contact"

            # return name and contact info for the current organization
            yield name, contact

    async def get_org_details(self, link):
        """Gets the CampusLabs organization details from a link to a CampusLabs organization.

        Args:
            link (str): the web link to the organization.

        Returns:
            tuple: (organization details, source link)
        """
        # get organization page
        future = self.loop.run_in_executor(None, requests.get, link)
        html_text = await future
        html_text = str(html_text.content)
        # tags that mark the beginning and end of the org. info json
        page_desc_begin = "window.initialAppState = "
        page_desc_end = ";</script>"
        # only get organization info json from the page content
        new_text = html_text[html_text.find(page_desc_begin) + len(page_desc_begin):]
        new_text = new_text[:new_text.find(page_desc_end)]
        # remove problematic quotes
        new_text = new_text.replace(r'\\"', '')
        # remove problematic backslashes
        new_text = new_text.replace('\\', '')
        # return org info and source link
        return json.loads(new_text), link
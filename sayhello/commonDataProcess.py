import os
import sys
from sayhello import app


class CommonDatabase:
    def __init__(self, url):
        self.url = os.path.dirname(app.root_path) + "/sayhello/commonData/" + url
        # self.url = "commonData/" + url
        self.comments = self.fetch()
        self.number = len(self.comments)

    def fetch(self):
        comments = {'PER': [], 'LOC': [], 'ORG': []}
        with open(self.url, mode="r") as file:
            for line in file:
                if "\n" in line:
                    line = line.rstrip("\n")
                # print(line)
                    line = line.split("@")
                    nen_type = line[1]
                    nen_body = line[0]
                # print(line)
                comments[nen_type].append(nen_body)

        print(comments)
        # print(n)
        return comments

    def commit(self):
        # Clear the original database
        with open(self.url, mode='w') as file:
            file.write("")

        out_list = []
        for i in self.comments.keys():
            comment_list = self.comments[i]
            for j in comment_list:
                this_string = "@".join([j]+[i])
                out_list.append(this_string)
        print(out_list)

        with open(self.url, mode='a') as file:
            for i in out_list:
                # print(i)
                file.write(i)
                file.write('\n')  # 换行

    def add(self, entity, typ):
        # Check repetition
        for i in self.comments.keys():
            # print(i, typ)
            # print(i == typ)
            if i == typ:
                if entity not in self.comments[i]:
                    self.comments[i].append(entity)
        # Commit to database
        return


"""d = CommonDatabase("nen.cmdata")
d.commit()
d.add("Cirilla", "PER")
d.commit()
"""

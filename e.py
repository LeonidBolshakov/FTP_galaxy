# def line_ending_handling(
#     text: str, end_line_author: str, end_line_prg: str, max_distance: int = 10
# ) -> str:
#     pos_text = 0
#     text_out = ""
#     while True:
#         pos_end_line_author = text.find(end_line_author, pos_text)
#         if pos_end_line_author == -1:
#             text_out += text[pos_text:]
#             break
#         else:
#             pos_end_line_prg = text.find(end_line_prg, pos_end_line_author)
#             if pos_end_line_prg == -1:
#                 text_out += text[pos_text:]
#                 break
#             if pos_end_line_prg - pos_end_line_author < max_distance:
#                 text_out += text[pos_text:pos_end_line_author] + " "
#             else:
#                 text_out += text[pos_text : pos_end_line_author + 1]
#             pos_text = pos_end_line_author + 1
#
#     return text_out
#
#
# print(line_ending_handling("1234567a901a345678b01234567ba", "a", "b"))

from docx import Document
from docx.shared import Cm, Inches
from docx.enum.section import WD_ORIENTATION
from docx.shared import Pt, Cm, Inches

doc: Document = Document()
section = doc.add_section()
section.top_margin = Cm(1)
print(len(doc.sections))

# import aspose.words as aw

# # create PDF load options
# loadOptions = aw.saving.PdfLoadOptions()
# loadOptions.load_format = aw.LoadFormat.PDF 

# # set index of the starting page and page count
# loadOptions.page_index = 0
# loadOptions.page_count = 1

# # skip images in PDF
# loadOptions.skip_pdf_images = True

# # to set password for encrypted PDF files
# #loadOptions.password = "12345" 

# # load PDF file
# doc = aw.Document("PDF.pdf", loadOptions)

# # convert PDF to Word
# doc.save("pdf-to-word.docx")
list_text_topic = []
a = '\n'.join(list_text_topic)
print('')
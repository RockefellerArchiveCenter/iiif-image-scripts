import img2pdf
import os

class PDFMaker:

    def make_pdf(self, derivative_dir):
        identifiers = self.get_identifiers(derivative_dir)
        for ident in identifiers:
            files = [os.path.join(derivative_dir, file) for file in sorted(os.listdir(derivative_dir)) if file.startswith(ident)]
            pdf_name = os.path.join(derivative_dir, ident)
            with open("{}.pdf".format(pdf_name),"wb") as f:
                f.write(img2pdf.convert(files))

    def get_identifiers(self, image_dir):
        """Get a list of unique identifiers from files in a directory.
        Args:
            image_dir (str): a string representation of the directory containing image files.
        Returns:
            identifiers (lst): a list of unique identifiers.
        """
        identifiers = [file.split('_')[0] for file in os.listdir(image_dir) if not file.startswith('.')]
        return list(set(identifiers))

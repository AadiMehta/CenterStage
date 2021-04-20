from django import forms  
class PostForm(forms.Form):  
    title = forms.CharField(label="Enter title",max_length=50)  
    text  = forms.CharField(label="Enter text ", max_length = 100) 

    def get_cleaned_data(self):
        data = {}
        data['title'] = self.cleaned_data['title']
        data['text'] = self.cleaned_data['text']
        return data
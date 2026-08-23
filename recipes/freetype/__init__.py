from pythonforandroid.recipes.freetype import FreetypeRecipe as _BaseFreetypeRecipe


class FreetypeRecipe(_BaseFreetypeRecipe):
    version = '2.13.2'
    url = 'https://sourceforge.net/projects/freetype/files/freetype2/{version}/freetype-{version}.tar.gz/download'


recipe = FreetypeRecipe()

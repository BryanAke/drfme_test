from mongoengine import (Document, EmbeddedDocument, StringField, ListField, ReferenceField, MapField,
                         ValidationError, EmbeddedDocumentField, IntField, DynamicField)
# Create your models here.
class Widget(Document):
    """
    Model for pretend data.
    """
    name = StringField()

    description = StringField()

    parent = ReferenceField('Widget')

    ancestors = ListField(ReferenceField('Widget'))

    relationships = ListField(EmbeddedDocumentField('Relationship'))

    meta = {
        'allow_inheritance': True
    }

    def addRelationship(self, reltype, widget):
        relationship = Relationship()
        relationship.subject_rel = self
        relationship.predicate = reltype
        relationship.object_rel = widget

        self.relationships.append(relationship)

    def set_parent(self, newparent):
        self.parent = newparent
        self.addRelationship("parent", newparent)
        newparent.addRelationship("child", self)

    def set_ancestors(self):
        self.ancestors = []
        if self.parent is not None:
            self.ancestors.append(self.parent)
            self.ancestors.extend(self.parent.ancestors)


class Relationship(EmbeddedDocument):
    subject_rel = ReferenceField("Widget")
    predicate = StringField()
    object_rel = ReferenceField("Widget")

class SpecialField(DynamicField):

    def __get__(self, instance, owner):
        if instance is None:
            # Document class being used rather than a document object
            return self

        value = instance._data.get(self.name)  # Get value from document instance if available

        #can't have any of that int crap.
        if isinstance(value, int):
            return str(value) + " MILLION DOLLARS!"
        return value

class SpecialWidget(Widget):
    """
    Model that inherits some of Widget's stuff and adds some data.
    """

    some_value = IntField()

    dyn_value = SpecialField()

    components = ListField(EmbeddedDocumentField("Component"))

class Component(EmbeddedDocument):

    name = StringField()

    some_thing = ReferenceField("Thing")


class ThingProps(EmbeddedDocument):

    value_one = StringField()
    value_two = StringField()
    value_three = IntField()

class Thing(Document):
    """
    A thing referenced by Components.
    """

    name = StringField()
    some_values = EmbeddedDocumentField("ThingProps")

    testmap = MapField(IntField())

Copyright (c) 2003 Infrae. All rights reserved.
Copyright (c) 2004 Plone Group and Contributors. All rights reserved.
See also LICENSE.txt

Meta::

  Valid for:  CMFMetadata 0.7.X
  Author:     Kapil Thangavelu
  Email:      <kapil@plone.org>
  CVS:        $Revision: 1.1 $

CMF Metadata

  Implemented Use Cases

    - Define Metadata

    - Map Metadata to a Content Type

    - Import Metadata Definition

    - Export Metadata Definition

    - Export Metadata for a Content Object

    - Import Metadata for a Content Object

    - Display a Form for Metadata

    - Validate Values for Metadata

    - Restrict Displayable/Editable Metadata based on
      permissions, roles, or state.

    - Containment Based Metadata Acquisition

    - Invoke Triggers upon Metadata Changes

    - Index/Search Metadata

    - Integrated Actions for Content Types (CMF Only)

  Todo Use Cases

    - Delegate Metadata Element to a different Definition.

    - Customize an Element of Metadata Set mapped onto a particular
      Content Type.

    - Upgrade/ChangeSet Engine for updating metadata sets.

    - Canonical/Standards Based XML Generation and Import for
      Metadata Sets.

  Design

    Storage/Annotations

      metadata storage is based on annotating content objects. metadata
      storage itself is partioned by set namespaces, and also includes
      a partition for metadata configuration on a per object basis.

    Definitions

      definitions of the metadata are conducted with the metadata tool zmi
      interface. these definitions are managed as sets composed of elements,
      with guards and fields attached to elements. these definitions can
      be exported and imported to xml and are used for validation and display
      of the metadata. these definitions are then mapped onto content types
      that they will be available for.

    Tool API

      the metadata tool api is fairly simple, the core of it is simply
      one method. getMetadata which returns a binding object, below.

      the additional methods are present to conform to the metadata tool
      api defined by the cmf interfaces.

    Binding/Adapter

      bindings functions as an adapter between the content object,
      the metadata definition, and the stored metdata values. it offers
      a unified api to the programmer to operate on an object's metadata,
      and unlike a service or tool, allows for security checks to be
      automatically performed in the context of the content object.

      additionally the binding adapter makes use of the metadata storage
      to store configuration options that can be set per object, that
      affect the runtime behavior of the binding. this capability is used
      to implement some of the advanced features of the metadata system
      such as metadata acquisition and mutation triggers, and can be
      extended as need arises.

    Indexing and Searching

      because metadata is stored in an object annotation, and accessed
      through a binding object, direct indexing of an object's metadata
      using the normal zcatalog indexes is not possible. The
      ProxyIndex product was developed to address the issue, and
      allows for the use of a tales expression to retrieve values for
      indexing. the metadata system automatically constructs indexes
      for a metadata set upon set initialization, using tales
      expressions to retrieve a binding and an element's value for
      a content object.

    Hook Points

      To allow for flexibility and customization based on a
      requirements the metadata system offers two major hook points
      exposed at by its python api.

      Access

        The Access hook is used by the metadata tool to construct
        a binding for a content object. access hooks can be registered
        on a per content type basis or as a default hook.

      Runtime Data Initializer

        When a metadata binding is constructed for an object with no
        metadata annotation data, a runtime data initializer is
        invoked to construct the binding's runtime data. initializers
        can be defined on a per content type basis or as a default
	initializer.


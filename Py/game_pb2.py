# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: Py/game.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='Py/game.proto',
  package='GT',
  syntax='proto3',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\rPy/game.proto\x12\x02GT\"*\n\x07PosVect\x12\t\n\x01x\x18\x01 \x01(\x05\x12\t\n\x01y\x18\x02 \x01(\x05\x12\t\n\x01z\x18\x03 \x01(\x05\"\x1e\n\tGameState\x12\x11\n\traceState\x18\x01 \x01(\x05\"\xb8\x01\n\x07Vehicle\x12\x10\n\x08\x65ngSpeed\x18\x01 \x01(\x05\x12\x10\n\x08\x65ngBoost\x18\x02 \x01(\x05\x12\x0f\n\x07\x65ngGear\x18\x03 \x01(\x05\x12\r\n\x05speed\x18\x04 \x01(\x05\x12\r\n\x05steer\x18\x05 \x01(\x11\x12\x0b\n\x03pos\x18\x06 \x01(\x05\x12\x11\n\tfLeftSlip\x18\x07 \x01(\x05\x12\x13\n\x0b\x66RighttSlip\x18\x08 \x01(\x05\x12\x11\n\trLeftSlip\x18\t \x01(\x05\x12\x12\n\nrRightSlip\x18\n \x01(\x05\"K\n\x06Screen\x12\x0c\n\x04\x64\x61ta\x18\x01 \x01(\x0c\x12\r\n\x05width\x18\x02 \x01(\x05\x12\x0e\n\x06height\x18\x03 \x01(\x05\x12\x14\n\x03\x62pp\x18\x04 \x01(\x0e\x32\x07.GT.BPP\"\x82\x01\n\x0bObservation\x12\x16\n\x02SS\x18\x01 \x01(\x0b\x32\n.GT.Screen\x12\x19\n\x02GS\x18\x02 \x01(\x0b\x32\r.GT.GameState\x12\x17\n\x02VS\x18\x03 \x01(\x0b\x32\x0b.GT.Vehicle\x12\r\n\x05\x66rame\x18\x04 \x01(\x05\x12\x18\n\x03pos\x18\x05 \x01(\x0b\x32\x0b.GT.PosVect*\x1d\n\x03\x42PP\x12\n\n\x06\x42PP_16\x10\x00\x12\n\n\x06\x42PP_24\x10\x01\x62\x06proto3'
)

_BPP = _descriptor.EnumDescriptor(
  name='BPP',
  full_name='GT.BPP',
  filename=None,
  file=DESCRIPTOR,
  create_key=_descriptor._internal_create_key,
  values=[
    _descriptor.EnumValueDescriptor(
      name='BPP_16', index=0, number=0,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='BPP_24', index=1, number=1,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=494,
  serialized_end=523,
)
_sym_db.RegisterEnumDescriptor(_BPP)

BPP = enum_type_wrapper.EnumTypeWrapper(_BPP)
BPP_16 = 0
BPP_24 = 1



_POSVECT = _descriptor.Descriptor(
  name='PosVect',
  full_name='GT.PosVect',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='x', full_name='GT.PosVect.x', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='y', full_name='GT.PosVect.y', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='z', full_name='GT.PosVect.z', index=2,
      number=3, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=21,
  serialized_end=63,
)


_GAMESTATE = _descriptor.Descriptor(
  name='GameState',
  full_name='GT.GameState',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='raceState', full_name='GT.GameState.raceState', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=65,
  serialized_end=95,
)


_VEHICLE = _descriptor.Descriptor(
  name='Vehicle',
  full_name='GT.Vehicle',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='engSpeed', full_name='GT.Vehicle.engSpeed', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='engBoost', full_name='GT.Vehicle.engBoost', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='engGear', full_name='GT.Vehicle.engGear', index=2,
      number=3, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='speed', full_name='GT.Vehicle.speed', index=3,
      number=4, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='steer', full_name='GT.Vehicle.steer', index=4,
      number=5, type=17, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='pos', full_name='GT.Vehicle.pos', index=5,
      number=6, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='fLeftSlip', full_name='GT.Vehicle.fLeftSlip', index=6,
      number=7, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='fRighttSlip', full_name='GT.Vehicle.fRighttSlip', index=7,
      number=8, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='rLeftSlip', full_name='GT.Vehicle.rLeftSlip', index=8,
      number=9, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='rRightSlip', full_name='GT.Vehicle.rRightSlip', index=9,
      number=10, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=98,
  serialized_end=282,
)


_SCREEN = _descriptor.Descriptor(
  name='Screen',
  full_name='GT.Screen',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='data', full_name='GT.Screen.data', index=0,
      number=1, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=b"",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='width', full_name='GT.Screen.width', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='height', full_name='GT.Screen.height', index=2,
      number=3, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='bpp', full_name='GT.Screen.bpp', index=3,
      number=4, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=284,
  serialized_end=359,
)


_OBSERVATION = _descriptor.Descriptor(
  name='Observation',
  full_name='GT.Observation',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='SS', full_name='GT.Observation.SS', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='GS', full_name='GT.Observation.GS', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='VS', full_name='GT.Observation.VS', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='frame', full_name='GT.Observation.frame', index=3,
      number=4, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='pos', full_name='GT.Observation.pos', index=4,
      number=5, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=362,
  serialized_end=492,
)

_SCREEN.fields_by_name['bpp'].enum_type = _BPP
_OBSERVATION.fields_by_name['SS'].message_type = _SCREEN
_OBSERVATION.fields_by_name['GS'].message_type = _GAMESTATE
_OBSERVATION.fields_by_name['VS'].message_type = _VEHICLE
_OBSERVATION.fields_by_name['pos'].message_type = _POSVECT
DESCRIPTOR.message_types_by_name['PosVect'] = _POSVECT
DESCRIPTOR.message_types_by_name['GameState'] = _GAMESTATE
DESCRIPTOR.message_types_by_name['Vehicle'] = _VEHICLE
DESCRIPTOR.message_types_by_name['Screen'] = _SCREEN
DESCRIPTOR.message_types_by_name['Observation'] = _OBSERVATION
DESCRIPTOR.enum_types_by_name['BPP'] = _BPP
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

PosVect = _reflection.GeneratedProtocolMessageType('PosVect', (_message.Message,), {
  'DESCRIPTOR' : _POSVECT,
  '__module__' : 'Py.game_pb2'
  # @@protoc_insertion_point(class_scope:GT.PosVect)
  })
_sym_db.RegisterMessage(PosVect)

GameState = _reflection.GeneratedProtocolMessageType('GameState', (_message.Message,), {
  'DESCRIPTOR' : _GAMESTATE,
  '__module__' : 'Py.game_pb2'
  # @@protoc_insertion_point(class_scope:GT.GameState)
  })
_sym_db.RegisterMessage(GameState)

Vehicle = _reflection.GeneratedProtocolMessageType('Vehicle', (_message.Message,), {
  'DESCRIPTOR' : _VEHICLE,
  '__module__' : 'Py.game_pb2'
  # @@protoc_insertion_point(class_scope:GT.Vehicle)
  })
_sym_db.RegisterMessage(Vehicle)

Screen = _reflection.GeneratedProtocolMessageType('Screen', (_message.Message,), {
  'DESCRIPTOR' : _SCREEN,
  '__module__' : 'Py.game_pb2'
  # @@protoc_insertion_point(class_scope:GT.Screen)
  })
_sym_db.RegisterMessage(Screen)

Observation = _reflection.GeneratedProtocolMessageType('Observation', (_message.Message,), {
  'DESCRIPTOR' : _OBSERVATION,
  '__module__' : 'Py.game_pb2'
  # @@protoc_insertion_point(class_scope:GT.Observation)
  })
_sym_db.RegisterMessage(Observation)


# @@protoc_insertion_point(module_scope)

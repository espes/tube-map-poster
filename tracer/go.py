import os
import sys
import ctypes
import traceback

from PIL import Image

from loader import Process

libcxx = ctypes.CDLL("libstdc++.6.dylib")
libcxx._ZNSsC1EPKcRKSaIcE.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]

class CxxString(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ('alloc_thing', ctypes.c_void_p),
        ('p', ctypes.c_void_p),
    ]

    def __init__(self, s):
        dummy_ret = ctypes.c_void_p()
        # std::basic_string<char, std::char_traits<char>, std::allocator<char> >::basic_string(char const*, std::allocator<char> const&)
        libcxx._ZNSsC1EPKcRKSaIcE(ctypes.pointer(self), ctypes.c_char_p(s), ctypes.pointer(dummy_ret))


class VmVectorizationSettings(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ('image_category', ctypes.c_uint32),
        ('image_quality', ctypes.c_uint32),
        ('adv_num_colors', ctypes.c_uint32),
        ('adv_color_sensitivity', ctypes.c_uint32),
        ('adv_use_palette_aa', ctypes.c_uint8),
        ('_pad_1', ctypes.c_uint8 * 3),
        ('adv_segmentation_complexity', ctypes.c_uint32),
        ('adv_min_num_pixels', ctypes.c_uint32),
        ('adv_anti_aliasing_rejection', ctypes.c_uint32),
        ('adv_cluster_colors', ctypes.c_uint8),
        ('_pad_2', ctypes.c_uint8 * 3),
        ('adv_contour_smoothness', ctypes.c_uint32),
        ('adv_detect_sharp_corners', ctypes.c_uint32),
        ('adv_curve_complexity', ctypes.c_uint32),
        ('adv_use_contour_aa', ctypes.c_uint8),
        ('_pad_3', ctypes.c_uint8 * 3),
        ('use_advanced_mode', ctypes.c_uint8),
        ('_pad_4', ctypes.c_uint8 * 3),
        ('toolaction_list', ctypes.c_void_p),
        ('_toolaction_list_unkn', ctypes.c_void_p),
        ('toolaction_list2', ctypes.c_void_p),
        ('_toolaction_list2_unkn', ctypes.c_void_p),
        ('colors_start', ctypes.c_void_p),
        ('colors_end', ctypes.c_void_p),
        ('_colors_unkn', ctypes.c_void_p),
        ('num_palette_colors', ctypes.c_uint32),
        ('palette_mode', ctypes.c_uint32),
        ('batch_num_colors', ctypes.c_uint32),
        ('flatten_image_mode', ctypes.c_int32),
        ('flatten_color1', ctypes.c_float),
        ('flatten_color2', ctypes.c_float),
        ('flatten_color3', ctypes.c_float),
        ('flatten_color4', ctypes.c_float),
        ('recommended_flatten_image_mode', ctypes.c_uint32),
    ]

# print ctypes.sizeof(VmVectorizationSettings)
assert(ctypes.sizeof(VmVectorizationSettings) == 0x94)



p=Process('/Applications/Vector Magic.app/Contents/MacOS/Vector Magic')


class ExporterSettings(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ('cake_stack_mode', ctypes.c_uint32),
        ('eps_compatibility_mode', ctypes.c_uint32),
        ('shape_stroking_mode', ctypes.c_uint32),
        ('dxf_mode', ctypes.c_uint32),
        ('vec1_start', ctypes.c_void_p),
        ('vec1_end', ctypes.c_void_p),
        ('vec1_end_of_storage', ctypes.c_void_p),
        ('vec1_bitvec_unkn', ctypes.c_void_p),
        ('vec2_bitvec_unkn2', ctypes.c_void_p),
        ('list1_start', ctypes.c_void_p),
        ('list1_end', ctypes.c_void_p),
        ('list2_start', ctypes.c_void_p),
        ('list2_end', ctypes.c_void_p),
    ]

# print ctypes.sizeof(VmVectorizationSettings)
assert(ctypes.sizeof(ExporterSettings) == 0x58)

esettings = ExporterSettings()
p_esettings = ctypes.cast(ctypes.pointer(esettings), ctypes.c_void_p).value

esettings.list1_start = p_esettings + ExporterSettings.list1_start.offset
esettings.list1_end = p_esettings + ExporterSettings.list1_start.offset
esettings.list2_start = p_esettings + ExporterSettings.list2_start.offset
esettings.list2_end = p_esettings + ExporterSettings.list2_start.offset


colors = [
    [  28,  63, 149 ], # blue top header
    [ 254, 254, 254 ], # white background
    [ 243, 243, 243 ], # grey background
    [ 232, 232, 232 ], # grey text
    [ 180, 179, 184 ], # free tram zone
    [ 209, 209, 209 ], # text border
    [ 198, 234, 252 ], # water blue
    [ 240,  46,  36 ], # roundal red
    [   1, 174, 239 ], # water edge
    [ 174,  99,  14 ], # bakerloo
    [ 240,  46,  38 ], # central
    [ 255, 209,   5 ], # circle
    [   1, 132,  64 ], # district
    [ 254, 135, 162 ], # h & c
    [ 147, 158, 159 ], # jubilee
    [ 150,   1,  91 ], # metro
    [ 35,   29,  31 ], # northern
    [   2, 155, 220 ], # victoria
    [ 132, 205, 188 ], # w & c
    [   3, 177, 176 ], # DLR
    [ 229,  26,  54 ], # air line
    [ 254, 128,  37 ], # overground
    [ 122, 193,  65 ], # trams
]

inpath = sys.argv[1]
print inpath

try:
    InitFunc_56 = 0x1001087F0
    p.call(InitFunc_56, [])

    InitFunc_57 = 0x100108AA0
    p.call(InitFunc_57, [])

    InitFunc_64 = 0x100127B10
    p.call(InitFunc_64, [])

    InitFunc_65 = 0x100127B10
    p.call(InitFunc_65, [])

    InitFunc_66 = 0x100135E70
    p.call(InitFunc_66, [])

    InitFunc_75 = 0x100154FA0
    p.call(InitFunc_75, [])

    settings = VmVectorizationSettings()
    p_settings = ctypes.cast(ctypes.pointer(settings), ctypes.c_void_p).value

    # VmVectorizationSettings::VmVectorizationSettings(VmVectorizationSettings_*this)
    _ZN23VmVectorizationSettingsC2Ev = 0x100080DD0
    p.call(_ZN23VmVectorizationSettingsC2Ev, [p_settings])

    settings.image_category = 1
    settings.image_quality = 1
    settings.adv_num_colors = 11
    settings.adv_color_sensitivity = 1
    settings.adv_use_palette_aa = 1 # True
    settings.adv_segmentation_complexity = 5
    settings.adv_min_num_pixels = 11
    settings.adv_anti_aliasing_rejection = 0
    settings.adv_cluster_colors = 1 # True
    settings.adv_contour_smoothness = 6
    settings.adv_detect_sharp_corners = 1
    settings.adv_curve_complexity = 6
    settings.adv_use_contour_aa = 1 # True
    settings.use_advanced_mode = 0 # False
    settings.num_palette_colors = len(colors)#14
    settings.palette_mode = 1
    settings.batch_num_colors = 0
    settings.flatten_image_mode = -1
    settings.recommended_flatten_image_mode = 0

    colors_arr = p.malloc(len(colors)*4*4)
    colors_ptr = ctypes.cast(colors_arr, ctypes.POINTER(ctypes.c_float))
    for i, (r,g,b) in enumerate(colors):
        # VmVectorisationSettings color components are reverse compared the Palette()
        colors_ptr[i*4 + 0] = 1.
        colors_ptr[i*4 + 1] = r/255.
        colors_ptr[i*4 + 2] = g/255.
        colors_ptr[i*4 + 3] = b/255.

    settings.colors_start = colors_arr
    settings.colors_end = colors_arr + len(colors)*4*4


    # VmController::VmController(VmController *this)
    _ZN12VmControllerC1Ev = 0x10014E3C0

    p_vmcontroller = p.malloc(0x170)
    p.call(_ZN12VmControllerC1Ev, [p_vmcontroller])

    p_vmcontroller_classification_type = p_vmcontroller + 0x08 # ImageClassification+0x08
    p_vmcontroller_classification_quality = p_vmcontroller + 0x0C # ImageClassification+0x0C
    p_vmcontroller_classification_palette_mode = p_vmcontroller + 0x10 #ImageClassification+0x18
    p_vmcontroller_classification_palette_num_colors = p_vmcontroller + 0x14 #ImageClassification+0x1C

    print "p_vmcontroller = 0x%08x" % p_vmcontroller

    pp_coreengine = p_vmcontroller + 0x108
    p_coreEngine = ctypes.cast(pp_coreengine, ctypes.POINTER(ctypes.c_ulong))[0]
    print "p_coreEngine = 0x%08x" % p_coreEngine

    p_paletteFinder = p_coreEngine + 0xB60
    print "p_paletteFinder = 0x%08x" % p_paletteFinder

    p_palette = p_coreEngine + 0x98

    p_segmenter = p_coreEngine + 0xE48
    p_subPixelSegmenter = p_segmenter + 0x78

    img = Image.open(inpath)
    # imgb = img.tobytes("raw", "ABGR")
    imgb = img.convert("RGBA").tobytes("raw", "BGRA")
    cpath = ctypes.c_char_p("img.png")
    cimgb = ctypes.c_char_p(imgb)

    p_path = ctypes.cast(cpath, ctypes.c_void_p).value
    p_imgb = ctypes.cast(cimgb, ctypes.c_void_p).value

    # VmController::loadImageFromMemory(const char* fn,  void* bits, int width, int height);
    _ZN12VmController19loadImageFromMemoryEPKcPKhii = 0x100151260
    r = p.call(_ZN12VmController19loadImageFromMemoryEPKcPKhii, [p_vmcontroller, p_path, p_imgb, img.width, img.height])
    assert r == 0

    if False:
        # VmController::classifyImage(VmController *this, const VmVectorizationSettings *)
        _ZN12VmController13classifyImageERK23VmVectorizationSettings = 0x10014FCF0
        r = p.call(_ZN12VmController13classifyImageERK23VmVectorizationSettings, [p_vmcontroller, p_settings])
        print r


        # classification_type = load32(p_vmcontroller_classification_type)
        # classification_quality = load32(p_vmcontroller_classification_quality)
        # classification_palette_mode = load32(p_vmcontroller_classification_palette_mode)
        # classification_palette_num_colors = load32(p_vmcontroller_classification_palette_num_colors)
        # hexdump(p_vmcontroller_imageclassification08, 8)
        # hexdump(p_vmcontroller_imageclassification18, 8)

        # print classification_type
        # print classification_quality
        # print classification_palette_mode
        # print classification_palette_num_colors

    if False:
        # VmController::findPalettes(VmController *this, const VmVectorizationSettings *, int range, int numColors)
        _ZN12VmController12findPalettesERK23VmVectorizationSettingsii = 0x1001500A0
        r = p.call(_ZN12VmController12findPalettesERK23VmVectorizationSettingsii, [p_vmcontroller, p_settings, 2, 12])
        print r

        # print "palette:"
        # hexdump(p_palette, 32)

        # print "wutptr:"
        # hexdump(p_subPixelSegmenter + 0x50, 8)

    print "segment..."
    # VmController::segmentImage(VmController *this, const VmVectorizationSettings *)
    _ZN12VmController12segmentImageERK23VmVectorizationSettings = 0x1001508D0
    r = p.call(_ZN12VmController12segmentImageERK23VmVectorizationSettings, [p_vmcontroller, p_settings])
    print r


    print "dumping segmentation..."
    # VmController::segmentationImagePointer(VmController * this)
    _ZN12VmController24segmentationImagePointerEv = 0x10014EFD0
    segPtr = p.call(_ZN12VmController24segmentationImagePointerEv, [p_vmcontroller])

    segdata = ctypes.string_at(segPtr, img.width*img.height*4)

    # print "written"
    Image.frombytes("RGBA", (img.width,img.height), segdata, "raw", "BGRA").save("segout.png")
    # print "saved"

    print "contour smooth..."
    # VmController::contourSmoothImage(VmController *this, const VmVectorizationSettings *)
    _ZN12VmController18contourSmoothImageERK23VmVectorizationSettings = 0x100150B30
    r = p.call(_ZN12VmController18contourSmoothImageERK23VmVectorizationSettings, [p_vmcontroller, p_settings])
    print r

    print "bezier fit..."
    # VmController::bezierFitImage(VmController *this, const VmVectorizationSettings *)
    _ZN12VmController14bezierFitImageERK23VmVectorizationSettings = 0x100150D40
    r = p.call(_ZN12VmController14bezierFitImageERK23VmVectorizationSettings, [p_vmcontroller, p_settings])
    print r


    outfs = CxxString(inpath+".out.svg")
    p_outfs = ctypes.cast(ctypes.pointer(outfs), ctypes.c_void_p).value
    # VmController::writeVectorFileW(std::string, ExporterSettings &)
    _ZN12VmController16writeVectorFileWESsR16ExporterSettings = 0x1001514C0
    r = p.call(_ZN12VmController16writeVectorFileWESsR16ExporterSettings, [p_vmcontroller, p_outfs, p_esettings])
    print r

except:
    traceback.print_exc()
    os._exit(1)
else:
    os._exit(0)


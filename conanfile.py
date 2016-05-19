from conans import ConanFile, CMake
from conans.tools import download, unzip
from os import unlink as rmfile
from os.path import join, dirname, realpath
from shutil import move

class CucumberCppConan(ConanFile):
    name = "cucumber-cpp"
    version = "0.3"
    url = "https://github.com/skizzay/conan-cucumber-cpp.git"
    generators = "cmake", "txt", "ycm"
    settings = "os", "compiler", "build_type", "arch"
    options = {"framework": ["boost", "cppspec", "gtest", "standalone"], "shared": [True, False]}
    default_options = "framework=standalone", "shared=True"
    requires = "Boost/1.60.0@lasote/stable"
    exports = "CMakeLists.txt", "cmake/*", "include/*", "src/*"

    _basename = "%s-%s" % (name, version)
    _gtest_version = "1.7.0"
    _cmake_flags_table = {
            "boost": ["CUKE_DISABLE_BOOST_TEST=OFF", "CUKE_DISABLE_CPPSPEC=ON", "CUKE_DISABLE_GTEST=ON", "CUKE_USE_STATIC_BOOST=OFF"],
            "cppspec": ["CUKE_DISABLE_BOOST_TEST=ON", "CUKE_DISABLE_CPPSPEC=OFF", "CUKE_DISABLE_GTEST=ON"],
            "gtest": ["CUKE_DISABLE_BOOST_TEST=ON", "CUKE_DISABLE_CPPSPEC=ON", "CUKE_DISABLE_GTEST=OFF", "GMOCK_VER=%s" % _gtest_version],
            "standalone": ["CUKE_DISABLE_BOOST_TEST=ON", "CUKE_DISABLE_CPPSPEC=ON", "CUKE_DISABLE_GTEST=ON"]
        }
    _default_cmake_flags = ["", "CUKE_CONAN_BUILD=ON", "CUKE_DISABLE_E2E_TESTS=ON", "CUKE_DISABLE_UNIT_TESTS=ON", "CUKE_ENABLE_EXAMPLES=OFF"]

    def config(self):
        self.options["Boost"].shared = self.options.shared
        if (self.options.framework == "gtest"):
            self.requires("gtest/%s@lasote/stable" % self._gtest_version)

    def build(self):
        cmake = CMake(self.settings)
        self._execute("cmake %s %s %s" % (self.conanfile_directory, cmake.command_line, self._cmake_flags))
        self._execute("cmake --build $PWD --target cucumber-cpp-nomain %s" % (cmake.build_config))

    def package(self):
        self.copy('*.hpp', src='include', dst='include', keep_path=True)
        self.copy('CMakeLists.txt')
        self.copy('libcucumber-cpp-nomain.a', src='src', dst='lib')

    def package_info(self):
        if self.settings.compiler == "gcc":
            self.cpp_info.exelinkflags += ['-Xlinker', '--no-as-needed']
        elif self.settings.compiler == "Visual Studio":
            self.cpp_info.defines.append("NOMINMAX")
        self.cpp_info.libs.append("cucumber-cpp-nomain")
        if self.options.shared:
            self.cpp_info.defines.append("BOOST_ALL_DYN_LINK")

    def _execute(self, command):
        self.output.info(command)
        self.run(command)

    @property
    def _cmake_flags(self):
        flags = self._default_cmake_flags + \
                self._cmake_flags_table[str(self.options.framework)]
        return " -D".join(flags)

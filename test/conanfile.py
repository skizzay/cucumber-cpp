from conans import ConanFile, CMake
from os.path import join

class CucumberCppPackageTest(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    requires = "cucumber-cpp/0.3@skizzay/testing"
    generators = "cmake"
    options = {"shared": [False, True]}
    default_options = "shared=True"

    def config(self):
        self.options["cucumber-cpp"].shared = self.options.shared
        self.options["cucumber-cpp"].framework = "gtest"

    def imports(self):
        self.copy("cucumber_tests", src="bin", dst="bin")

    def build(self):
        cmake = CMake(self.settings)
        self.run("cmake %s %s" % (self.conanfile_directory, cmake.command_line))
        self.run("cmake --build $PWD %s" % (cmake.build_config))

    def test(self):
        self.run(join(".", "bin", "find_cucumber_tests"))

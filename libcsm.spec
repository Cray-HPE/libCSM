#
# MIT License
#
# (C) Copyright 2022-2023 Hewlett Packard Enterprise Development LP
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#

# Auto-generate RPM dependencies based on the Python project.
%{?python_enable_dependency_generator}

%define doc_dir /usr/share/doc/%(echo $NAME)/
%define doc_example_dir %{doc_dir}examples/
%define install_dir /usr/lib/%(echo $NAME)/
%define install_shell_dir %{install_dir}sh

# Define which Python flavors python-rpm-macros will use (this can be a list).
# https://github.com/openSUSE/python-rpm-macros#terminology
%define pythons %(echo $PYTHON_BIN)

# python*-devel is not listed because our build environments install Python from source and not from OS packaging.
BuildRequires: python-rpm-generators
BuildRequires: python-rpm-macros
Name: %(echo $NAME)
BuildArch: %(echo $ARCH)
License: MIT License
Summary: A library for providing common functions to Cray System Management procedures and operations.
Version: %(echo $VERSION)
Release: 1
Source: %{name}-%{version}.tar.bz2
Vendor: Hewlett Packard Enterprise Development LP
Provides: python%{python_version_nodots}-%(echo $NAME) = %{version}-%{release}
Provides: %(echo $NAME) = %{version}-%{release}
%python_subpackages

%description
A library for providing common functions to
Cray System Management procedures and operations.

%prep
%autosetup -p1 -n %{name}-%{version}

%build
# Install setuptools_scm[toml] so any context in this RPM build can resolve the module version.
%python_exec -m pip install -U setuptools_scm[toml]

# Build a source distribution.
%python_exec -m pip install -U build
%python_exec -m build --sdist

# Ensure a wheel is built.
%pyproject_wheel

%install
%pyproject_install

install -d -m 755 %{buildroot}%{doc_example_dir}
cp -pvr ./examples/* %{buildroot}%{doc_example_dir} | awk '{print $3}' | sed "s/'//g" | sed "s|$RPM_BUILD_ROOT||g" | tee -a INSTALLED_FILES

install -d -m 755 %{buildroot}%{install_shell_dir}
cp -pvr ./sh/* %{buildroot}%{install_shell_dir} | awk '{print $3}' | sed "s/'//g" | sed "s|$RPM_BUILD_ROOT||g" | tee -a INSTALLED_FILES
cat INSTALLED_FILES | xargs -i sh -c 'test -L {} && exit || test -f $RPM_BUILD_ROOT/{} && echo {} || echo %dir {}' | sort -u > FILES

%clean

%files %{python_files} -f FILES
%{python3_sitearch}/*
%docdir %{doc_dir}
%docdir %{doc_example_dir}
%doc README.adoc
%defattr(755,root,root)
%dir %{install_dir}
%license LICENSE

%changelog

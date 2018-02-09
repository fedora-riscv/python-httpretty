%if 0%{?fedora} || 0%{?rhel} > 7
# escaping for EPEL.
%global with_python3 1
%endif

%global github_owner    gabrielfalcao
%global github_name     HTTPretty
%global modname         httpretty
# define these only if actually building from a GH snapshot not a release tarball
%global github_commit   70af1f8cf925ef50cb5e72212fb0aa46e1451dc3
%global shortcommit     %(c=%{github_commit}; echo ${c:0:7})
%global github_date     20161011

%global run_tests 1

Name:           python-httpretty
Version:        0.8.14
# If github_date is defined, assume a post-release snapshot
Release:        7%{?github_date:.%{github_date}git%{shortcommit}}%{?dist}
Summary:        HTTP request mock tool for Python

License:        MIT
URL:            http://falcao.it/HTTPretty/
Source0:        https://github.com/%{github_owner}/%{github_name}/archive/%{github_commit}/%{github_name}-%{shortcommit}.tar.gz
# Alternative for building from a release tarball
#Source0:        https://files.pythonhosted.org/packages/source/h/httpretty/httpretty-%{version}.tar.gz

# Fix HTTPS with recent openssl
# This is https://github.com/gabrielfalcao/HTTPretty/pull/313
# Squashed by checking the PR branch out from git and doing:
# git diff master > pr313.patch (because just getting 313.patch from github
# results in a patch that doesn't apply)
# I edited the patch to apply several fixes:
# 1. Rename the `_socket` arg of the `fake_wrap_socket` function to `sock`
#    (as otherwise it breaks due to urllib3 calling `wrap_socket` with the
#    socket arg named as `sock`)
# 2. In test_passthrough.py, correct the type of the expected response
#    (requests `Response.content` is a bytestring, not a string)
# 3. Remove the addition of `test_httpretty_should_passthrough_for_ssl`,
#    as it requires a remote trip
# 4. Use {0} ({1}, {2}...) in format strings, not just {}, as {} doesn't
#    work in Python 2.6 (EPEL 6)
# 5. Try importing skip from unittest2 if it's not available from unittest
#    (Python 2.6 unittest didn't have it)
# I've noted all these issues in comments on the PR
Patch0:         pr313.patch

# Fix tests with Python 3
Patch1:         https://github.com/gabrielfalcao/HTTPretty/pull/314.patch

# Avoid unnecessary remote access requirement (note: test only actually
# does a remote connection after PR #313)
Patch2:         python-httpretty-fakesock_getpeercert_noconnect.patch

# Fix a couple of issues with urllib 1.10 (as found in RHEL 6)
# https://github.com/gabrielfalcao/HTTPretty/pull/315
Patch3:         0001-Handle-bugs-in-older-urllib3-versions-in-one-of-the-.patch

# Fix setUp and tearDown not calling reset
# https://github.com/gabrielfalcao/HTTPretty/pull/317
Patch4:         0001-Call-reset-from-setUp-and-tearDown-in-addition-to-en.patch

BuildArch:      noarch

BuildRequires:  python2-devel
BuildRequires:  python-setuptools
# For tests
BuildRequires:  python-httplib2
BuildRequires:  python-mock
BuildRequires:  python-nose
BuildRequires:  python-requests
BuildRequires:  python-sure
BuildRequires:  python-urllib3
BuildRequires:  python-tornado
%if 0%{?epel} == 6
# Need unittest2 to get the 'skip' decorator
BuildRequires:  python-unittest2
%endif

%global _description\
Once upon a time a python developer wanted to use a RESTful API, everything was\
fine but until the day he needed to test the code that hits the RESTful API:\
what if the API server is down? What if its content has changed?\
\
Don't worry, HTTPretty is here for you.

%description %_description

%package -n python2-httpretty
Summary: %summary
Requires:       python-urllib3
%{?python_provide:%python_provide python2-httpretty}

%description -n python2-httpretty %_description

%if 0%{?with_python3}
%package -n python3-httpretty
Summary:        HTTP request mock tool for Python 3
Requires:       python3-urllib3

BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
# For tests
BuildRequires:  python3-httplib2
BuildRequires:  python3-mock
BuildRequires:  python3-nose
BuildRequires:  python3-requests
BuildRequires:  python3-sure
BuildRequires:  python3-urllib3
BuildRequires:  python3-tornado

%description -n python3-httpretty
Once upon a time a python developer wanted to use a RESTful API, everything was
fine but until the day he needed to test the code that hits the RESTful API:
what if the API server is down? What if its content has changed?

Don't worry, HTTPretty is here for you.
%endif

%prep
%autosetup -n %{github_name}-%{github_commit} -p1

# Alternative for building from a release tarball
#autosetup -n httpretty-%{version} -p1

# un-pin requirements
sed -i -e 's/==.*//g' development.txt test-requirements.txt requirements.txt
sed -i -e 's/requests\[security\]/requests/g' development.txt
# remove some 'requirements' that aren't actually needed just for us to run tests
sed -i -e '/^coverage/d' development.txt test-requirements.txt
sed -i -r -e '/^(S|s)phinx/d' development.txt
sed -i -e '/^rednose/d' development.txt
sed -i -e '/^nose-randomly/d' development.txt
sed -i -e '/^flake8/d' development.txt
sed -i -e '/^ipdb/d' development.txt
# These tests require a remote roundtrip, so remove them
rm tests/unit/test_passthrough.py

%if 0%{?with_python3}
rm -rf %{py3dir}
cp -a . %{py3dir}
%endif

%build
# setup.py contains non-ASCII characters; in Koji build environment
# default encoding is ASCII and this will choke, so set a UTF-8 locale
LANG=en_US.UTF-8 %py2_build

%if 0%{?with_python3}
pushd %{py3dir}
LANG=en_US.UTF-8 %py3_build
popd
%endif

%install
rm -rf $RPM_BUILD_ROOT
LANG=en_US.UTF-8 %py2_install

%if 0%{?with_python3}
pushd %{py3dir}
LANG=en_US.UTF-8 %py3_install
popd
%endif


%check
%if %{run_tests}
LANG=en_US.UTF-8 %{__python2} setup.py test

%if 0%{?with_python3}
pushd %{py3dir}
LANG=en_US.UTF-8 %{__python3} setup.py test
popd
%endif
%endif


%files -n python2-httpretty
%doc README.md
%license COPYING
%{python_sitelib}/httpretty
%{python_sitelib}/httpretty-%{version}-py2.?.egg-info

%if 0%{?with_python3}
%files -n python3-httpretty
%doc README.md
%license COPYING
%{python3_sitelib}/httpretty
%{python3_sitelib}/httpretty-%{version}-py3.?.egg-info
%endif


%changelog
* Fri Feb 09 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.8.14-7.20161011git70af1f8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Fri Sep 29 2017 Troy Dawson <tdawson@redhat.com> - 0.8.14-6.20161011git70af1f8
- Cleanup spec file conditionals

* Sat Aug 19 2017 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 0.8.14-5.20161011git70af1f8
- Python 2 binary package renamed to python2-httpretty
  See https://fedoraproject.org/wiki/FinalizingFedoraSwitchtoPython3

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.8.14-4.20161011git70af1f8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.8.14-3.20161011git70af1f8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Fri Jan 27 2017 Adam Williamson <awilliam@redhat.com> - 0.8.14-2.20161011git70af1f8
- Backport PR #317 (call reset from setUp / tearDown) - thanks gholms

* Fri Jan 06 2017 Adam Williamson <awilliam@redhat.com> - 0.8.14-1.20161011git70af1f8
- Update to current git master (as a 0.8.14 post-release snapshot)
- Backport PR #313 (fix with recent OpenSSL, requests and urllib3)
- Backport PR #314 (fix a test with Python 3)
- Backport PR #315 (fix some issues with urllib 1.10, as found in RHEL 6)
- Avoid an unnecessary remote roundtrip in one of the tests
- Replace dependency 'un-pinning' patch with some sed commands in the spec
- Replace ASCII patch by running setup.py with a UTF-8 LANG
- Enable the tests, with necessary buildrequires

* Tue Dec 13 2016 Charalampos Stratakis <cstratak@redhat.com> - 0.8.3-8
- Rebuild for Python 3.6

* Tue Jul 19 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.8.3-7
- https://fedoraproject.org/wiki/Changes/Automatic_Provides_for_Python_RPM_Packages

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 0.8.3-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Tue Nov 10 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.8.3-5
- Rebuilt for https://fedoraproject.org/wiki/Changes/python3.5

* Thu Jun 18 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.8.3-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Mon Mar 02 2015 Jamie Lennox <jamielennox@redhat.com> - 0.8.3-3
- Added conditional __python2 macros for building on RHEL 6.

* Tue Feb 24 2015 Jamie Lennox <jamielennox@redhat.com> - 0.8.3-2
- Added with_python3 build flags to enable building on EPEL.

* Mon Jul 28 2014 Jamie Lennox <jamielennox@redhat.com> - 0.8.3-1
- Updated to new version.
- Removed check, there are simply too many problems upstream.

* Mon Mar 10 2014 Jamie Lennox <jamielennox@redhat.com> - 0.8.0-1
- Initial package.


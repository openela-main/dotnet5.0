%bcond_with bootstrap

# Avoid provides/requires from private libraries
%global privlibs             libhostfxr
%global privlibs %{privlibs}|libclrjit
%global privlibs %{privlibs}|libcoreclr
%global privlibs %{privlibs}|libcoreclrtraceptprovider
%global privlibs %{privlibs}|libdbgshim
%global privlibs %{privlibs}|libhostpolicy
%global privlibs %{privlibs}|libmscordaccore
%global privlibs %{privlibs}|libmscordbi
%global privlibs %{privlibs}|libsos
%global privlibs %{privlibs}|libsosplugin
%global __provides_exclude ^(%{privlibs})\\.so
%global __requires_exclude ^(%{privlibs})\\.so

# LTO triggers a compilation error for a source level issue.  Given that LTO should not
# change the validity of any given source and the nature of the error (undefined enum), I
# suspect a generator program is mis-behaving in some way.  This needs further debugging,
# until that's done, disable LTO.  This has to happen before setting the flags below.
%define _lto_cflags %{nil}

%global host_version 5.0.17
%global runtime_version 5.0.17
%global aspnetcore_runtime_version %{runtime_version}
%global sdk_version 5.0.214
%global templates_version %{runtime_version}
#%%global templates_version %%(echo %%{runtime_version} | awk 'BEGIN { FS="."; OFS="." } {print $1, $2, $3+1 }')

%global host_rpm_version %{host_version}
%global aspnetcore_runtime_rpm_version %{aspnetcore_runtime_version}
%global runtime_rpm_version %{runtime_version}
%global sdk_rpm_version %{sdk_version}

# upstream can update releases without revving the SDK version so these don't always match
%global src_version %{sdk_version}

%if 0%{?fedora} || 0%{?rhel} < 8
%global use_bundled_libunwind 0
%else
%global use_bundled_libunwind 1
%endif

%ifarch aarch64
%global use_bundled_libunwind 1
%endif

%ifarch x86_64
%global runtime_arch x64
%endif
%ifarch aarch64
%global runtime_arch arm64
%endif

%{!?runtime_id:%global runtime_id %(. /etc/os-release ; echo "${ID}.${VERSION_ID%%.*}")-%{runtime_arch}}

Name:           dotnet5.0
Version:        %{sdk_rpm_version}
Release:        1%{?dist}
Summary:        .NET Runtime and SDK
License:        MIT and ASL 2.0 and BSD and LGPLv2+ and CC-BY and CC0 and MS-PL and EPL-1.0 and GPL+ and GPLv2 and ISC and OFL and zlib
URL:            https://github.com/dotnet/

# The source is generated on a RHEL/Fedora box via:
# ./build-dotnet-tarball v%%{src_version}-SDK
Source0:        dotnet-v%{src_version}-SDK.tar.gz
Source1:        check-debug-symbols.py
Source2:        dotnet.sh.in

Patch1:         source-build-remove-test-references-from-patches.patch

Patch100:       runtime-62170-clang13.patch

# Disable telemetry by default; make it opt-in
Patch500:       sdk-telemetry-optout.patch

%if 0%{?fedora} > 32 || 0%{?rhel} > 8
ExclusiveArch:  aarch64 x86_64
%else
ExclusiveArch:  x86_64
%endif


BuildRequires:  clang
BuildRequires:  cmake
BuildRequires:  coreutils
BuildRequires:  dotnet-sdk-5.0
%if %{without bootstrap}
BuildRequires:  dotnet5.0-build-reference-packages
BuildRequires:  dotnet-sdk-5.0-source-built-artifacts
%endif
BuildRequires:  findutils
BuildRequires:  git
%if 0%{?fedora} || 0%{?rhel} > 7
BuildRequires:  glibc-langpack-en
%endif
BuildRequires:  hostname
BuildRequires:  krb5-devel
BuildRequires:  libcurl-devel
BuildRequires:  libicu-devel
%if ! %{use_bundled_libunwind}
BuildRequires:  libunwind-devel
%endif
BuildRequires:  lldb-devel
BuildRequires:  llvm
BuildRequires:  lttng-ust-devel
BuildRequires:  make
BuildRequires:  openssl-devel
BuildRequires:  python3
BuildRequires:  systemtap-sdt-devel
BuildRequires:  tar
BuildRequires:  zlib-devel

%description
.NET is a fast, lightweight and modular platform for creating
cross platform applications that work on Linux, macOS and Windows.

It particularly focuses on creating console applications, web
applications and micro-services.

.NET contains a runtime conforming to .NET Standards a set of
framework libraries, an SDK containing compilers and a 'dotnet'
application to drive everything.


%package -n dotnet

Version:        %{sdk_rpm_version}
Summary:        .NET CLI tools and runtime

Requires:       dotnet-sdk-5.0%{?_isa} >= %{sdk_rpm_version}-%{release}

%description -n dotnet
.NET is a fast, lightweight and modular platform for creating
cross platform applications that work on Linux, macOS and Windows.

It particularly focuses on creating console applications, web
applications and micro-services.

.NET contains a runtime conforming to .NET Standards a set of
framework libraries, an SDK containing compilers and a 'dotnet'
application to drive everything.


%package -n dotnet-host

Version:        %{host_rpm_version}
Summary:        .NET command line launcher

%description -n dotnet-host
The .NET host is a command line program that runs a standalone
.NET application or launches the SDK.

.NET is a fast, lightweight and modular platform for creating
cross platform applications that work on Linux, Mac and Windows.

It particularly focuses on creating console applications, web
applications and micro-services.


%package -n dotnet-hostfxr-5.0

Version:        %{host_rpm_version}
Summary:        .NET command line host resolver

# Theoretically any version of the host should work. But lets aim for the one
# provided by this package, or from a newer version of .NET
Requires:       dotnet-host%{?_isa} >= %{host_rpm_version}-%{release}

%description -n dotnet-hostfxr-5.0
The .NET host resolver contains the logic to resolve and select
the right version of the .NET SDK or runtime to use.

.NET is a fast, lightweight and modular platform for creating
cross platform applications that work on Linux, Mac and Windows.

It particularly focuses on creating console applications, web
applications and micro-services.


%package -n dotnet-runtime-5.0

Version:        %{runtime_rpm_version}
Summary:        NET 5.0 runtime

Requires:       dotnet-hostfxr-5.0%{?_isa} >= %{host_rpm_version}-%{release}

# libicu is dlopen()ed
Requires:       libicu%{?_isa}

# See src/runtime.*/src/libraries/Native/AnyOS/brotli-version.txt
Provides:       bundled(brotli) = 1.0.9
%if %{use_bundled_libunwind}
Provides: bundled(libunwind) = 1.3
%endif

%description -n dotnet-runtime-5.0
The .NET runtime contains everything needed to run .NET applications.
It includes a high performance Virtual Machine as well as the framework
libraries used by .NET applications.

.NET is a fast, lightweight and modular platform for creating
cross platform applications that work on Linux, Mac and Windows.

It particularly focuses on creating console applications, web
applications and micro-services.


%package -n aspnetcore-runtime-5.0

Version:        %{aspnetcore_runtime_rpm_version}
Summary:        ASP.NET Core 5.0 runtime

Requires:       dotnet-runtime-5.0%{?_isa} >= %{runtime_rpm_version}-%{release}

%description -n aspnetcore-runtime-5.0
The ASP.NET Core runtime contains everything needed to run .NET
web applications. It includes a high performance Virtual Machine as
well as the framework libraries used by .NET applications.

ASP.NET Core is a fast, lightweight and modular platform for creating
cross platform web applications that work on Linux, Mac and Windows.

It particularly focuses on creating console applications, web
applications and micro-services.


%package -n dotnet-templates-5.0

Version:        %{sdk_rpm_version}
Summary:        .NET 5.0 templates

# Theoretically any version of the host should work. But lets aim for the one
# provided by this package, or from a newer version of .NET
Requires:       dotnet-host%{?_isa} >= %{host_rpm_version}-%{release}

%description -n dotnet-templates-5.0
This package contains templates used by the .NET SDK.

.NET is a fast, lightweight and modular platform for creating
cross platform applications that work on Linux, Mac and Windows.

It particularly focuses on creating console applications, web
applications and micro-services.


%package -n dotnet-sdk-5.0

Version:        %{sdk_rpm_version}
Summary:        .NET 5.0 Software Development Kit

Provides:       bundled(js-jquery)
Provides:       bundled(npm)

Requires:       dotnet-runtime-5.0%{?_isa} >= %{runtime_rpm_version}-%{release}
Requires:       aspnetcore-runtime-5.0%{?_isa} >= %{aspnetcore_runtime_rpm_version}-%{release}

Requires:       dotnet-apphost-pack-5.0%{?_isa} >= %{runtime_rpm_version}-%{release}
Requires:       dotnet-targeting-pack-5.0%{?_isa} >= %{runtime_rpm_version}-%{release}
Requires:       aspnetcore-targeting-pack-5.0%{?_isa} >= %{aspnetcore_runtime_rpm_version}-%{release}
Requires:       netstandard-targeting-pack-2.1%{?_isa} >= %{sdk_rpm_version}-%{release}

Requires:       dotnet-templates-5.0%{?_isa} >= %{sdk_rpm_version}-%{release}

%description -n dotnet-sdk-5.0
The .NET SDK is a collection of command line applications to
create, build, publish and run .NET applications.

.NET is a fast, lightweight and modular platform for creating
cross platform applications that work on Linux, Mac and Windows.

It particularly focuses on creating console applications, web
applications and micro-services.


%global dotnet_targeting_pack() %{expand:
%package -n %{1}

Version:        %{2}
Summary:        Targeting Pack for %{3} %{4}

Requires:       dotnet-host%{?_isa}

%description -n %{1}
This package provides a targeting pack for %{3} %{4}
that allows developers to compile against and target %{3} %{4}
applications using the .NET SDK.

%files -n %{1}
%dir %{_libdir}/dotnet/packs
%{_libdir}/dotnet/packs/%{5}
}

%dotnet_targeting_pack dotnet-apphost-pack-5.0 %{runtime_rpm_version} Microsoft.NETCore.App 5.0 Microsoft.NETCore.App.Host.%{runtime_id}
%dotnet_targeting_pack dotnet-targeting-pack-5.0 %{runtime_rpm_version} Microsoft.NETCore.App 5.0 Microsoft.NETCore.App.Ref
%dotnet_targeting_pack aspnetcore-targeting-pack-5.0 %{aspnetcore_runtime_rpm_version} Microsoft.AspNetCore.App 5.0 Microsoft.AspNetCore.App.Ref
#%%dotnet_targeting_pack netstandard-targeting-pack-2.1 %%{sdk_rpm_version} NETStandard.Library 2.1 NETStandard.Library.Ref


%package -n dotnet-sdk-5.0-source-built-artifacts

Version:        %{sdk_rpm_version}
Summary:        Internal package for building .NET 5.0 Software Development Kit

%description -n dotnet-sdk-5.0-source-built-artifacts
The .NET source-built archive is a collection of packages needed
to build the .NET SDK itself.

These are not meant for general use.


%prep
%setup -q -n dotnet-v%{src_version}-SDK

%if %{without bootstrap}
# Remove all prebuilts
find -iname '*.dll' -type f -delete
find -iname '*.so' -type f -delete
find -iname '*.tar.gz' -type f -delete
find -iname '*.nupkg' -type f -delete
find -iname '*.zip' -type f -delete
rm -rf .dotnet/
rm -rf packages/source-built
%endif

%if %{without bootstrap}
mkdir -p packages/archive
ln -s %{_libdir}/dotnet/source-built-artifacts/*.tar.gz packages/archive/
ln -s %{_libdir}/dotnet/reference-packages/Private.SourceBuild.ReferencePackages*.tar.gz packages/archive
%endif

# Fix bad hardcoded path in build
sed -i 's|/usr/share/dotnet|%{_libdir}/dotnet|' src/dotnet-runtime.*/src/installer/corehost/cli/hostmisc/pal.unix.cpp

# Disable warnings
sed -i 's|skiptests|skiptests ignorewarnings|' repos/runtime.common.props

%patch1 -p1

pushd src/dotnet-runtime.*
%patch100 -p1
popd

pushd src/dotnet-sdk.*
%patch500 -p1
popd

%ifnarch x86_64
mkdir -p artifacts/obj/%{runtime_arch}/Release
cp artifacts/obj/x64/Release/PackageVersions.props artifacts/obj/%{runtime_arch}/Release/PackageVersions.props
%endif

cat source-build-info.txt

find -iname 'nuget.config' -exec echo {}: \; -exec cat {} \; -exec echo \;


%build
cat /etc/os-release

cp -a %{_libdir}/dotnet previously-built-dotnet
%if %{without bootstrap}
# We need to create a copy because we will mutate this
%endif

%if 0%{?fedora} > 32 || 0%{?rhel} > 8
# Setting this macro ensures that only clang supported options will be
# added to ldflags and cflags.
%global toolchain clang
%set_build_flags
%else
# Filter flags not supported by clang
%global dotnet_cflags %(echo %optflags | sed -re 's/-specs=[^ ]*//g')
%global dotnet_ldflags %(echo %{__global_ldflags} | sed -re 's/-specs=[^ ]*//g')
export CFLAGS="%{dotnet_cflags}"
export CXXFLAGS="%{dotnet_cflags}"
export LDFLAGS="%{dotnet_ldflags}"
%endif
 
%ifarch aarch64
# -mbranch-protection=standard breaks unwinding in CoreCLR through libunwind
CFLAGS=$(echo $CFLAGS | sed -e 's/-mbranch-protection=standard //')
CXXFLAGS=$(echo $CXXFLAGS | sed -e 's/-mbranch-protection=standard //')
%endif
 
# -fstack-clash-protection breaks CoreCLR
CFLAGS=$(echo $CFLAGS  | sed -e 's/-fstack-clash-protection//' )
CXXFLAGS=$(echo $CXXFLAGS  | sed -e 's/-fstack-clash-protection//' )

export EXTRA_CFLAGS="$CFLAGS"
export EXTRA_CXXFLAGS="$CXXFLAGS"
export EXTRA_LDFLAGS="$LDFLAGS"

unset CFLAGS
unset CXXFLAGS
unset LDFLAGS

#%%if %%{without bootstrap}
#  --with-ref-packages %%{_libdir}/dotnet/reference-packages/ \
#  --with-packages %%{_libdir}/dotnet/source-built-artifacts/*.tar.gz \
#  --with-sdk %%{_libdir}/dotnet \
#%%endif

VERBOSE=1 ./build.sh \
    --with-sdk previously-built-dotnet \
%if %{without bootstrap}
%endif
    -- \
    /v:n \
    /p:SkipPortableRuntimeBuild=true \
    /p:LogVerbosity=n \
    /p:MinimalConsoleLogOutput=false \
    /p:ContinueOnPrebuiltBaselineError=true \
%if %{use_bundled_libunwind}
    /p:UseSystemLibunwind=false \
%else
    /p:UseSystemLibunwind=true \
%endif


sed -e 's|[@]LIBDIR[@]|%{_libdir}|g' %{SOURCE2} > dotnet.sh


%install
install -dm 0755 %{buildroot}%{_libdir}/dotnet
ls artifacts/%{runtime_arch}/Release
tar xf artifacts/%{runtime_arch}/Release/dotnet-sdk-%{sdk_version}-%{runtime_id}.tar.gz -C %{buildroot}%{_libdir}/dotnet/

# Install managed symbols
tar xf artifacts/%{runtime_arch}/Release/runtime/dotnet-runtime-symbols-%{runtime_version}-%{runtime_id}.tar.gz \
    -C %{buildroot}/%{_libdir}/dotnet/shared/Microsoft.NETCore.App/%{runtime_version}/

# Fix executable permissions on files
find %{buildroot}%{_libdir}/dotnet/ -type f -name '*.a' -exec chmod -x {} \;
find %{buildroot}%{_libdir}/dotnet/ -type f -name '*.dll' -exec chmod -x {} \;
find %{buildroot}%{_libdir}/dotnet/ -type f -name '*.h' -exec chmod -x {} \;
find %{buildroot}%{_libdir}/dotnet/ -type f -name '*.pdb' -exec chmod -x {} \;
find %{buildroot}%{_libdir}/dotnet/ -type f -name '*.props' -exec chmod -x {} \;
find %{buildroot}%{_libdir}/dotnet/ -type f -name '*.pubxml' -exec chmod -x {} \;
find %{buildroot}%{_libdir}/dotnet/ -type f -name '*.targets' -exec chmod -x {} \;
find %{buildroot}%{_libdir}/dotnet/ -type f -name '*.xml' -exec chmod -x {} \;
chmod 0755 %{buildroot}/%{_libdir}/dotnet/sdk/%{sdk_version}/AppHostTemplate/apphost
chmod 0755 %{buildroot}/%{_libdir}/dotnet/packs/Microsoft.NETCore.App.Host.%{runtime_id}/%{runtime_version}/runtimes/%{runtime_id}/native/apphost
chmod 0755 %{buildroot}/%{_libdir}/dotnet/packs/Microsoft.NETCore.App.Host.%{runtime_id}/%{runtime_version}/runtimes/%{runtime_id}/native/libnethost.so
chmod 0644 %{buildroot}/%{_libdir}/dotnet/packs/Microsoft.NETCore.App.Host.%{runtime_id}/%{runtime_version}/runtimes/%{runtime_id}/native/nethost.h
chmod 0755 %{buildroot}/%{_libdir}/dotnet/packs/Microsoft.NETCore.App.Host.%{runtime_id}/%{runtime_version}/runtimes/%{runtime_id}/native/singlefilehost

# Provided by dotnet-host from another SRPM
#install -dm 0755 %%{buildroot}%%{_sysconfdir}/profile.d/
#install dotnet.sh %%{buildroot}%%{_sysconfdir}/profile.d/

# Provided by dotnet-host from another SRPM
#install -dm 0755 %%{buildroot}/%%{_datadir}/bash-completion/completions
# dynamic completion needs the file to be named the same as the base command
#install src/dotnet-sdk.*/scripts/register-completions.bash %%{buildroot}/%%{_datadir}/bash-completion/completions/dotnet

# TODO: the zsh completion script needs to be ported to use #compdef
#install -dm 755 %%{buildroot}/%%{_datadir}/zsh/site-functions
#install src/cli/scripts/register-completions.zsh %%{buildroot}/%%{_datadir}/zsh/site-functions/_dotnet

# Provided by dotnet-host from another SRPM
#install -dm 0755 %%{buildroot}%%{_bindir}
#ln -s ../../%%{_libdir}/dotnet/dotnet %%{buildroot}%%{_bindir}/

# Provided by dotnet-host from another SRPM
#install -dm 0755 %%{buildroot}%%{_mandir}/man1/
#find -iname 'dotnet*.1' -type f -exec cp {} %%{buildroot}%%{_mandir}/man1/ \;

# Provided by dotnet-host from another SRPM
#echo "%%{_libdir}/dotnet" >> install_location
#install -dm 0755 %%{buildroot}%%{_sysconfdir}/dotnet
#install install_location %%{buildroot}%%{_sysconfdir}/dotnet/

install -dm 0755 %{buildroot}%{_libdir}/dotnet/source-built-artifacts
install artifacts/%{runtime_arch}/Release/Private.SourceBuilt.Artifacts.*.tar.gz %{buildroot}/%{_libdir}/dotnet/source-built-artifacts/

# Check debug symbols in all elf objects. This is not in %%check
# because native binaries are stripped by rpm-build after %%install.
# So we need to do this check earlier.
echo "Testing build results for debug symbols..."
%{SOURCE1} -v %{buildroot}%{_libdir}/dotnet/

# Self-check
%{buildroot}%{_libdir}/dotnet/dotnet --info

# Provided by dotnet-host from another SRPM
rm %{buildroot}%{_libdir}/dotnet/LICENSE.txt
rm %{buildroot}%{_libdir}/dotnet/ThirdPartyNotices.txt
rm %{buildroot}%{_libdir}/dotnet/dotnet

# Provided by netstandard-targeting-pack-2.1 from another SRPM
rm -rf %{buildroot}%{_libdir}/dotnet/packs/NETStandard.Library.Ref/2.1.0


%files -n dotnet-hostfxr-5.0
%dir %{_libdir}/dotnet/host/fxr
%{_libdir}/dotnet/host/fxr/%{host_version}

%files -n dotnet-runtime-5.0
%dir %{_libdir}/dotnet/shared
%dir %{_libdir}/dotnet/shared/Microsoft.NETCore.App
%{_libdir}/dotnet/shared/Microsoft.NETCore.App/%{runtime_version}

%files -n aspnetcore-runtime-5.0
%dir %{_libdir}/dotnet/shared
%dir %{_libdir}/dotnet/shared/Microsoft.AspNetCore.App
%{_libdir}/dotnet/shared/Microsoft.AspNetCore.App/%{aspnetcore_runtime_version}

%files -n dotnet-templates-5.0
%dir %{_libdir}/dotnet/templates
%{_libdir}/dotnet/templates/%{templates_version}

%files -n dotnet-sdk-5.0
%dir %{_libdir}/dotnet/sdk
%{_libdir}/dotnet/sdk/%{sdk_version}
%dir %{_libdir}/dotnet/packs

%files -n dotnet-sdk-5.0-source-built-artifacts
%dir %{_libdir}/dotnet
%{_libdir}/dotnet/source-built-artifacts


%changelog
* Thu May 05 2022 Omair Majid <omajid@redhat.com> - 5.0.214-1
- Update to .NET SDK 5.0.214 and Runtime 5.0.17
- Resolves: RHBZ#2082258

* Thu Apr 28 2022 Omair Majid <omajid@redhat.com> - 5.0.213-2
- Update to .NET SDK 5.0.213 and Runtime 5.0.16
- Resolves: RHBZ#2080053

* Wed Mar 23 2022 Omair Majid <omajid@redhat.com> - 5.0.212-2
- Update to .NET SDK 5.0.212 and Runtime 5.0.15
- Resolves: RHBZ#2060495

* Wed Mar 23 2022 Omair Majid <omajid@redhat.com> - 5.0.211-1
- Update to .NET SDK 5.0.211 and Runtime 5.0.14
- Resolves: RHBZ#2047766

* Wed Jan 05 2022 Omair Majid <omajid@redhat.com> - 5.0.210-2
- Update to .NET SDK 5.0.210 and Runtime 5.0.13
- Resolves: RHBZ#2030737

* Thu Dec 02 2021 Omair Majid <omajid@redhat.com> - 5.0.209-2
- Bump release
- Related: RHBZ#2011058
- Related: RHBZ#2003078

* Sun Nov 21 2021 Omair Majid <omajid@redhat.com> - 5.0.209.1-1
- Update to .NET SDK 5.0.209 and Runtime 5.0.12
- Resolves: RHBZ#2024319
- Resolves: RHBZ#2011058
- Resolves: RHBZ#2003078

* Thu Aug 12 2021 Omair Majid <omajid@redhat.com> - 5.0.206-1
- Update to .NET SDK 5.0.206 and Runtime 5.0.9
- Resolves: RHBZ#1990940

* Tue Aug 10 2021 Omair Majid <omajid@redhat.com> - 5.0.205-1
- Update to .NET SDK 5.0.205 and Runtime 5.0.8
- Resolves: RHBZ#1985445

* Fri Jun 11 2021 Omair Majid <omajid@redhat.com> - 5.0.204-1
- Update to .NET SDK 5.0.204 and Runtime 5.0.7
- Resolves: RHBZ#1966164
- Resolves: RHBZ#1966996

* Fri Jun 11 2021 Omair Majid <omajid@redhat.com> - 5.0.203-1
- Update to .NET SDK 5.0.203 and Runtime 5.0.6
- Resolves: RHBZ#1954327

* Thu Apr 22 2021 Omair Majid <omajid@redhat.com> - 5.0.202-2
- Update to .NET SDK 5.0.202 and Runtime 5.0.5
- Create -source-built-artifacts subpackage
- Resolves: RHBZ#1947600

* Wed Feb 10 2021 Omair Majid <omajid@redhat.com> - 5.0.103-2
- Update to .NET SDK 5.0.103 and Runtime 5.0.3
- Resolves: RHBZ#1924762

* Wed Jan 13 2021 Omair Majid <omajid@redhat.com> - 5.0.102-2
- Update to .NET SDK 5.0.102 and Runtime 5.0.2
- Resolves: RHBZ#1912569

* Thu Dec 03 2020 Omair Majid <omajid@redhat.com> - 5.0.100-0.10.20201203git337413b
- Update to latest commit of .NET Core SDK 5.0.100 and Runtime 5.0.0
- Resolves: RHBZ#1897362

* Thu Nov 12 2020 Omair Majid <omajid@redhat.com> - 5.0.100-0.9
- Update to a work-in-progres .NET 5 GA build
- Resolves: RHBZ#1897362

* Mon Oct 26 2020 Omair Majid <omajid@redhat.com> - 5.0.100-0.8.rc1
- Bump version
- Resolves: RHBZ#1891094

* Fri Oct 23 2020 Omair Majid <omajid@redhat.com> - 5.0.100-0.7.rc1
- Update to .NET Core SDK 5.0.100 RC1 and Runtime 5.0.0 RC1
- Resolves: RHBZ#1891094

* Tue Sep 15 2020 Omair Majid <omajid@redhat.com> - 5.0.100-0.6.preview8
- Switch to a smaller tarball
- Fix restore-with-rid
- Resolves: RHBZ#1835019

* Mon Sep 14 2020 Omair Majid <omajid@redhat.com> - 5.0.100-0.5.preview8
- Fix package descriptions
- Fix permissions in installed files
- Resolves: RHBZ#1835019

* Fri Sep 11 2020 Omair Majid <omajid@redhat.com> - 5.0.100-0.4.preview8
- Update to .NET SDK 5.0 Preview 8
- Remove "Core" from descriptions
- Resolves: RHBZ#1835019

* Fri Aug 21 2020 Omair Majid <omajid@redhat.com> - 5.0.100-0.3.preview4
- Generate new source tarball with test files removed.
- Resolves: RHBZ#1835019

* Thu Aug 06 2020 Omair Majid <omajid@redhat.com> - 5.0.100-0.2.preview4
- Backport cmake compatiblity fix

* Fri Jul 10 2020 Omair Majid <omajid@redhat.com> - 5.0.100-0.2.preview4
- Fix building with custom CFLAGS/CXXFLAGS/LDFLAGS
- Clean up patches

* Mon Jul 06 2020 Omair Majid <omajid@redhat.com> - 5.0.100-0.1.preview4
- Initial build

* Sat Jun 27 2020 Omair Majid <omajid@redhat.com> - 3.1.105-4
- Disable bootstrap

* Fri Jun 26 2020 Omair Majid <omajid@redhat.com> - 3.1.105-3
- Re-bootstrap aarch64

* Fri Jun 19 2020 Omair Majid <omajid@redhat.com> - 3.1.105-3
- Disable bootstrap

* Thu Jun 18 2020 Omair Majid <omajid@redhat.com> - 3.1.105-1
- Bootstrap aarch64

* Tue Jun 16 2020 Chris Rummel <crummel@microsoft.com> - 3.1.105-1
- Update to .NET Core Runtime 3.1.5 and SDK 3.1.105

* Fri Jun 05 2020 Chris Rummel <crummel@microsoft.com> - 3.1.104-1
- Update to .NET Core Runtime 3.1.4 and SDK 3.1.104

* Thu Apr 09 2020 Chris Rummel <crummel@microsoft.com> - 3.1.103-1
- Update to .NET Core Runtime 3.1.3 and SDK 3.1.103

* Mon Mar 16 2020 Omair Majid <omajid@redhat.com> - 3.1.102-1
- Update to .NET Core Runtime 3.1.2 and SDK 3.1.102

* Fri Feb 28 2020 Omair Majid <omajid@redhat.com> - 3.1.101-4
- Disable bootstrap

* Fri Feb 28 2020 Omair Majid <omajid@redhat.com> - 3.1.101-3
- Enable bootstrap
- Add Fedora 33 runtime ids

* Thu Feb 27 2020 Omair Majid <omajid@redhat.com> - 3.1.101-2
- Disable bootstrap

* Tue Jan 21 2020 Omair Majid <omajid@redhat.com> - 3.1.101-1
- Update to .NET Core Runtime 3.1.1 and SDK 3.1.101

* Thu Dec 05 2019 Omair Majid <omajid@redhat.com> - 3.1.100-1
- Update to .NET Core Runtime 3.1.0 and SDK 3.1.100

* Mon Nov 18 2019 Omair Majid <omajid@redhat.com> - 3.1.100-0.4.preview3
- Fix apphost permissions

* Fri Nov 15 2019 Omair Majid <omajid@redhat.com> - 3.1.100-0.3.preview3
- Update to .NET Core Runtime 3.1.0-preview3.19553.2 and SDK
  3.1.100-preview3-014645

* Wed Nov 06 2019 Omair Majid <omajid@redhat.com> - 3.1.100-0.2
- Update to .NET Core 3.1 Preview 2

* Wed Oct 30 2019 Omair Majid <omajid@redhat.com> - 3.1.100-0.1
- Update to .NET Core 3.1 Preview 1

* Thu Oct 24 2019 Omair Majid <omajid@redhat.com> - 3.0.100-5
- Add cgroupv2 support to .NET Core

* Wed Oct 16 2019 Omair Majid <omajid@redhat.com> - 3.0.100-4
- Include fix from coreclr for building on Fedora 32

* Wed Oct 16 2019 Omair Majid <omajid@redhat.com> - 3.0.100-3
- Harden built binaries to pass annocheck

* Fri Oct 11 2019 Omair Majid <omajid@redhat.com> - 3.0.100-2
- Export DOTNET_ROOT in profile to make apphost lookup work

* Fri Sep 27 2019 Omair Majid <omajid@redhat.com> - 3.0.100-1
- Update to .NET Core Runtime 3.0.0 and SDK 3.0.100

* Wed Sep 25 2019 Omair Majid <omajid@redhat.com> - 3.0.100-0.18.rc1
- Update to .NET Core Runtime 3.0.0-rc1-19456-20 and SDK 3.0.100-rc1-014190

* Tue Sep 17 2019 Omair Majid <omajid@redhat.com> - 3.0.100-0.16.preview9
- Fix files duplicated between dotnet-apphost-pack-3.0 and dotnet-targeting-pack-3.0
- Fix dependencies between .NET SDK and the targeting packs

* Mon Sep 16 2019 Omair Majid <omajid@redhat.com> - 3.0.100-0.15.preview9
- Update to .NET Core Runtime 3.0.0-preview 9 and SDK 3.0.100-preview9

* Mon Aug 19 2019 Omair Majid <omajid@redhat.com> - 3.0.100-0.11.preview8
- Update to .NET Core Runtime 3.0.0-preview8-28405-07 and SDK
  3.0.100-preview8-013656

* Tue Jul 30 2019 Omair Majid <omajid@redhat.com> - 3.0.100-0.9.preview7
- Update to .NET Core Runtime 3.0.0-preview7-27912-14 and SDK
  3.0.100-preview7-012821

* Fri Jul 26 2019 Omair Majid <omajid@redhat.com> - 3.0.100-0.8.preview7
- Update to .NET Core Runtime 3.0.0-preview7-27902-19 and SDK
  3.0.100-preview7-012802

* Wed Jun 26 2019 Omair Majid <omajid@redhat.com> - 3.0.0-0.7.preview6
- Obsolete dotnet-sdk-3.0.1xx
- Add supackages for targeting packs
- Add -fcf-protection to CFLAGS

* Wed Jun 26 2019 Omair Majid <omajid@redhat.com> - 3.0.0-0.6.preview6
- Update to .NET Core Runtime 3.0.0-preview6-27804-01 and SDK 3.0.100-preview6-012264
- Set dotnet installation location in /etc/dotnet/install_location
- Update targeting packs
- Install managed symbols
- Completely conditionalize libunwind bundling

* Tue May 07 2019 Omair Majid <omajid@redhat.com> - 3.0.0-0.3.preview4
- Update to .NET Core 3.0 preview 4

* Tue Dec 18 2018 Omair Majid <omajid@redhat.com> - 3.0.0-0.1.preview1
- Update to .NET Core 3.0 preview 1

* Fri Dec 07 2018 Omair Majid <omajid@redhat.com> - 2.2.100
- Update to .NET Core 2.2.0

* Wed Nov 07 2018 Omair Majid <omajid@redhat.com> - 2.2.100-0.2.preview3
- Update to .NET Core 2.2.0-preview3

* Fri Nov 02 2018 Omair Majid <omajid@redhat.com> - 2.1.403-3
- Add host-fxr-2.1 subpackage

* Mon Oct 15 2018 Omair Majid <omajid@redhat.com> - 2.1.403-2
- Disable telemetry by default
- Users have to manually export DOTNET_CLI_TELEMETRY_OPTOUT=0 to enable

* Tue Oct 02 2018 Omair Majid <omajid@redhat.com> - 2.1.403-1
- Update to .NET Core Runtime 2.1.5 and SDK 2.1.403

* Wed Sep 26 2018 Omair Majid <omajid@redhat.com> - 2.1.402-2
- Add ~/.dotnet/tools to $PATH to make it easier to use dotnet tools

* Thu Sep 13 2018 Omair Majid <omajid@redhat.com> - 2.1.402-1
- Update to .NET Core Runtime 2.1.4 and SDK 2.1.402

* Wed Sep 05 2018 Omair Majid <omajid@redhat.com> - 2.1.401-2
- Use distro-standard flags when building .NET Core

* Tue Aug 21 2018 Omair Majid <omajid@redhat.com> - 2.1.401-1
- Update to .NET Core Runtime 2.1.3 and SDK 2.1.401

* Mon Aug 20 2018 Omair Majid <omajid@redhat.com> - 2.1.302-1
- Update to .NET Core Runtime 2.1.2 and SDK 2.1.302

* Fri Jul 20 2018 Omair Majid <omajid@redhat.com> - 2.1.301-1
- Update to .NET Core 2.1

* Thu May 03 2018 Omair Majid <omajid@redhat.com> - 2.0.7-1
- Update to .NET Core 2.0.7

* Wed Mar 28 2018 Omair Majid <omajid@redhat.com> - 2.0.6-2
- Enable bash completion for dotnet
- Remove redundant buildrequires and requires

* Wed Mar 14 2018 Omair Majid <omajid@redhat.com> - 2.0.6-1
- Update to .NET Core 2.0.6

* Fri Feb 23 2018 Omair Majid <omajid@redhat.com> - 2.0.5-1
- Update to .NET Core 2.0.5

* Wed Jan 24 2018 Omair Majid <omajid@redhat.com> - 2.0.3-5
- Don't apply corefx clang warnings fix on clang < 5

* Fri Jan 19 2018 Omair Majid <omajid@redhat.com> - 2.0.3-4
- Add a test script to sanity check debug and symbol info.
- Build with clang 5.0
- Make main package real instead of using a virtual provides (see RHBZ 1519325)

* Wed Nov 29 2017 Omair Majid <omajid@redhat.com> - 2.0.3-3
- Add a Provides for 'dotnet'
- Fix conditional macro

* Tue Nov 28 2017 Omair Majid <omajid@redhat.com> - 2.0.3-2
- Fix build on Fedora 27

* Fri Nov 17 2017 Omair Majid <omajid@redhat.com> - 2.0.3-1
- Update to .NET Core 2.0.3

* Thu Oct 19 2017 Omair Majid <omajid@redhat.com> - 2.0.0-4
- Add a hack to let omnisharp work

* Wed Aug 30 2017 Omair Majid <omajid@redhat.com> - 2.0.0-3
- Add a patch for building coreclr and core-setup correctly on Fedora >= 27

* Fri Aug 25 2017 Omair Majid <omajid@redhat.com> - 2.0.0-2
- Move libicu/libcurl/libunwind requires to runtime package
- Make sdk depend on the exact version of the runtime package

* Thu Aug 24 2017 Omair Majid <omajid@redhat.com> - 2.0.0-1
- Update to 2.0.0 final release

* Wed Jul 26 2017 Omair Majid <omajid@redhat.com> - 2.0.0-0.3.preview2
- Add man pages

* Tue Jul 25 2017 Omair Majid <omajid@redhat.com> - 2.0.0-0.2.preview2
- Add Requires on libicu
- Split into multiple packages
- Do not repeat first-run message

* Fri Jul 21 2017 Omair Majid <omajid@redhat.com> - 2.0.0-0.1.preview2
- Update to .NET Core 2.0 Preview 2

* Thu Mar 16 2017 Nemanja Milošević <nmilosevnm@gmail.com> - 1.1.0-7
- rebuilt with latest libldb
* Wed Feb 22 2017 Nemanja Milosevic <nmilosev@fedoraproject.org> - 1.1.0-6
- compat-openssl 1.0 for F26 for now
* Sun Feb 19 2017 Nemanja Milosevic <nmilosev@fedoraproject.org> - 1.1.0-5
- Fix wrong commit id's
* Sat Feb 18 2017 Nemanja Milosevic <nmilosev@fedoraproject.org> - 1.1.0-4
- Use commit id's instead of branch names
* Sat Feb 18 2017 Nemanja Milosevic <nmilosev@fedoraproject.org> - 1.1.0-3
- Improper patch5 fix
* Sat Feb 18 2017 Nemanja Milosevic <nmilosev@fedoraproject.org> - 1.1.0-2
- SPEC cleanup
- git removal (using all tarballs for reproducible builds)
- more reasonable versioning
* Thu Feb 09 2017 Nemanja Milosevic <nmilosev@fedoraproject.org> - 1.1.0-1
- Fixed debuginfo going to separate package (Patch1)
- Added F25/F26 RIL and fixed the version info (Patch2)
- Added F25/F26 RIL in Microsoft.NETCore.App suported runtime graph (Patch3)
- SPEC file cleanup
* Wed Jan 11 2017 Nemanja Milosevic <nmilosev@fedoraproject.org> - 1.1.0-0
- Initial RPM for Fedora 25/26.

<div id="top"></div>

<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]


<br />
<div align="center">

<h3 align="center">Nix Check Build Merge</h3>

  <p align="center">
    This project will allow you to check for build failures all the nixpkgs you maintain 
    <br />
    <a href="https://github.com/gador/nix-check-build-merge/issues">Report Bug</a>
    ·
    <a href="https://github.com/gador/nix-check-build-merge/issues">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

This is an early stage draft of a project with the goals of making maintaining and reviewing of packages in the Nix ecosystem easier than it currently is. It will consist of a backend server component and a simple web frontend. In its early stage, it should allow the automatic (re)building of the maintained packages of the given user and report build failures. 
In later stages it is planed to also help review new PR's, hopefully in a more automated way.

<p align="right">(<a href="#top">back to top</a>)</p>



### Built With

* [Nix](https://www.nixos.org/)
* [Python](https://www.python.org)

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

Currently, this is project is just in the draft phase. If you really want to take look around, clone this repo and run 
```sh
nix develop .
```
if you have flakes enabled, or run
```sh
nix-shell
```
if not.

Alternatively, you can build and run it locally with
```sh
nix build github:gador/nix-check-build-merge
```

### Prerequisites

Currently, this project was only tested and build on NixOS. If you have nix, it should also work.

### Installation

1. Install nix/NixOS.
2. Clone the repo
   ```sh
   git clone https://github.com/gador/nix-check-build-merge.git
   ```
3. Run the shell
   ```sh
   nix develop . # for flakes
   nix-shell # for non-flakes
   ```
<p align="right">(<a href="#top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

To display all maintained packages by a given user, issue:
```shell
nixcbm MAINTAINER --nixpkgs NIXPKGS_PATH
```
where MAINTAINER is the handle you are looking for and NIXPKGS_PATH is the path to the local nixpkgs repo.

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

- [ ] Backend
  - [ ] Automatically list all packages with a given name
  - [ ] Build the packages locally (maybe even periodically) 
  - [ ] git fetch current nixpkgs master
  - [ ] hydra-check the packages maintained
  - [ ] Add a sqlite backend to save the hydra-status and the local build status
    - [ ] Save build and hydra status along with the commit
  - [ ] Add a GitHub API access to list open PRs (with the usual filter criteria for reviewing PRs)
  - [ ] List top ten PRs which are ready to be reviewed
  - [ ] Add an option to build those PRs locally (like nixpkgs-review)
  - [ ] Add a way to post the result, comment, approve and/or merge PRs (like nixpkgs-review)
- [ ] Frontend 
    - [ ] Add a simple (flask?) web frontend with a static hello page
    - [ ] Add a list of maintained packages, along with a date and a commit of nixpkgs
    - [ ] Add a column with build status locally, as well as hydra
    - [ ] Add a link to the local build log and the hydra online log
    - [ ] List maintained packages with either green, yellow or red badge
    - [ ] List PRs ready to be reviewed, with links to them
    - [ ] Add an option to build them locally
    - [ ] Link the build log and add a badge for the build status

See the [open issues](https://github.com/gador/nix-check-build-merge/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- CONTRIBUTING -->
## Contributing

If you like this idea and want to help out, please consider opening a bug/feature report and list your ideas.
In this very early stage PRs are not really useful, because all the code needs to be written, anyway.

Before committing, please run `pre-commit` to apply import sorting and black code check.

Obviously later, I'll greatly appreciate any code improvements and bug mitigations ;-)

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- CONTACT -->
## Contact

Florian Brandes - [@twitter_handle](https://twitter.com/twitter_handle) - florian.brandes@posteo.de 

Project Link: [https://github.com/gador/nix-check-build-merge](https://github.com/gador/nix-check-build-merge)

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* [Readme template](https://github.com/othneildrew/Best-README-Template)

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[issues-shield]: https://img.shields.io/github/issues/gador/nix-check-build-merge.svg?style=for-the-badge
[issues-url]: https://github.com/gador/nix-check-build-merge/issues
[license-shield]: https://img.shields.io/github/license/gador/nix-check-build-merge.svg?style=for-the-badge
[license-url]: https://github.com/gador/nix-check-build-merge/blob/master/LICENSE.txt

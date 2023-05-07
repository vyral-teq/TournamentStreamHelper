LoadEverything().then(() => {
  gsap.config({ nullTargetWarn: false, trialWarn: false });

  let startingAnimation = gsap
    .timeline({ paused: true })
    .from([".logo"], { duration: 0.5, autoAlpha: 0, ease: "power2.inOut" }, 0.5)
    .from(
      [".floating .anim_container_outer"],
      {
        duration: 1,
        width: "0",
        ease: "power2.inOut",
      },
      1
    )
    .from(
      [".floating .base_container_outer"],
      {
        duration: 1,
        width: 0,
        ease: "power2.inOut",
      },
      1
    );

  Start = async () => {
    startingAnimation.restart();
  };

  Update = async (event) => {
    let data = event.data;
    let oldData = event.oldData;

    if (Object.keys(data.score.team["1"].player).length == 1) {
      for (const [t, team] of [
        data.score.team["1"],
        data.score.team["2"],
      ].entries()) {
        for (const [p, player] of [team.player["1"]].entries()) {
          if (player) {
            SetInnerHtml(
              $(`.p${t + 1}.container .name`),
              // For p2, place pronoun before name
              // For p1, place pronoun after name
              `
                ${
                  t == 1
                    ? `
                    <span class="pronoun">
                      ${player.pronoun ? player.pronoun : ""}
                    </span>
                  `
                    : ""
                }
                <span class="sponsor">
                  ${player.team ? player.team : ""}
                </span>
                ${await Transcript(player.name)}
                ${
                  t == 0
                    ? `
                    <span class="pronoun">
                      ${player.pronoun ? player.pronoun : ""}
                    </span>
                  `
                    : ""
                }
                ${team.losers ? "<span class='losers'>L</span>" : ""}
              `
            );

            let teamMultiplyier = t == 0 ? 1 : -1;

            await CharacterDisplay(
              $(`.p${t + 1}.character_container`),
              {
                source: `score.team.${t + 1}`,
                anim_out: {
                  autoAlpha: 0,
                  x: -20 * teamMultiplyier + "px",
                  stagger: teamMultiplyier * 0.2,
                  duration: 0.4,
                },
                anim_in: {
                  autoAlpha: 1,
                  x: "0px",
                  stagger: teamMultiplyier * 0.2,
                  duration: 0.4,
                },
              },
              event
            );

            SetInnerHtml(
              $(`.p${t + 1}.container .flagcountry`),
              player.country.asset
                ? `<div class='flag' style='background-image: url(../../${player.country.asset.toLowerCase()})'></div>`
                : ""
            );

            SetInnerHtml(
              $(`.p${t + 1}.container .flagstate`),
              player.state.asset
                ? `<div class='flag' style='background-image: url(../../${player.state.asset})'></div>`
                : ""
            );

            SetInnerHtml(
              $(`.p${t + 1}.container .sponsor_icon`),
              player.sponsor_logo
                ? `<div style='background-image: url(../../${player.sponsor_logo})'></div>`
                : ""
            );

            SetInnerHtml(
              $(`.p${t + 1}.container .avatar`),
              player.avatar
                ? `<div style="background-image: url('../../${player.avatar}')"></div>`
                : ""
            );

            SetInnerHtml(
              $(`.p${t + 1}.container .online_avatar`),
              player.online_avatar
                ? `<div style="background-image: url('${player.online_avatar}')"></div>`
                : ""
            );

            SetInnerHtml(
              $(`.p${t + 1}.container .twitter`),
              player.twitter
                ? `<span class="twitter_logo"></span>${String(player.twitter)}`
                : ""
            );

            let score = [data.score.score_left, data.score.score_right];

            SetInnerHtml($(`.p${t + 1}.container .score`), String(team.score));

            SetInnerHtml(
              $(`.p${t + 1}.container .sponsor-container`),
              `<div class='sponsor-logo' style='background-image: url(../../${player.sponsor_logo})'></div>`
            );
          }
        }
      }
    } else {
      for (const [t, team] of [
        data.score.team["1"],
        data.score.team["2"],
      ].entries()) {
        let teamName = "";

        if (!team.teamName || team.teamName == "") {
          let names = [];
          for (const [p, player] of Object.values(team.player).entries()) {
            if (player && player.name) {
              names.push(await Transcript(player.name));
            }
          }
          teamName = names.join(" / ");
        } else {
          teamName = team.teamName;
        }

        let teamMultiplyier = t == 0 ? 1 : -1;

        await CharacterDisplay(
          $(`.p${t + 1}.character_container`),
          {
            source: `score.team.${t + 1}`,
            anim_out: {
              autoAlpha: 0,
              x: -20 * teamMultiplyier + "px",
              stagger: teamMultiplyier * 0.2,
              duration: 0.4,
            },
            anim_in: {
              autoAlpha: 1,
              x: "0px",
              stagger: teamMultiplyier * 0.2,
              duration: 0.4,
            },
          },
          event
        );

        SetInnerHtml(
          $(`.p${t + 1}.container .name`),
          `
            ${teamName}
            ${team.losers ? "<span class='losers'>L</span>" : ""}
          `
        );

        let player = team.player["1"];

        SetInnerHtml(
          $(`.p${t + 1}.container .flagcountry`),
          player.country.asset ? `` : ""
        );

        SetInnerHtml(
          $(`.p${t + 1}.container .flagstate`),
          player.state.asset ? `` : ""
        );

        SetInnerHtml(
          $(`.p${t + 1}.container .sponsor_icon`),
          player.sponsor_logo ? `` : ""
        );

        SetInnerHtml(
          $(`.p${t + 1}.container .avatar`),
          player.avatar ? `` : ""
        );

        SetInnerHtml(
          $(`.p${t + 1}.container .online_avatar`),
          player.online_avatar ? `` : ""
        );

        SetInnerHtml(
          $(`.p${t + 1}.container .twitter`),
          player.twitter
            ? `<span class="twitter_logo"></span>${String(player.twitter)}`
            : ""
        );

        let score = [data.score.score_left, data.score.score_right];

        SetInnerHtml($(`.p${t + 1}.container .score`), String(team.score));

        SetInnerHtml(
          $(`.p${t + 1}.container .sponsor-container`),
          `<div class='sponsor-logo' style='background-image: url(../../${player.sponsor_logo})'></div>`
        );
      }
    }

    SetInnerHtml(
      $(".tournament_name"),
      data.tournamentInfo.tournamentName + " - " + data.tournamentInfo.eventName
    );

    SetInnerHtml($(".phase"), data.score.phase);
    SetInnerHtml($(".match"), data.score.match);
    SetInnerHtml(
      $(".best_of"),
      data.score.best_of_text ? data.score.best_of_text : ""
    );
  };
});

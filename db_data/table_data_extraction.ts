import { winter, trad, sport, boulder } from './raw_tables.ts';
import { writeFile } from 'fs/promises';

type importhtmls = {
  html1: string;
  html2: string;
  html3: string;
};

type imports = {
  winter: importhtmls;
  sport: importhtmls;
  trad: importhtmls;
  boulder: importhtmls;
};

const imports: imports = { winter, trad, sport, boulder };

const Arr = ['winter', 'trad', 'sport', 'boulder'];

type crag = {
  aspect: String;
  rockType: String;
  long: String;
  lat: String;
  name: String;
  numStaredClimbs: String;
  ukcLink: String;
};

const regexs: {
  aspect: RegExp;
  rockType: RegExp;
  long: RegExp;
  lat: RegExp;
  name: RegExp;
  numStaredClimbs: RegExp;
  ukcLink: RegExp;
} = {
  aspect: /Faces:<\/strong> <small>(.*)<\/small><br>/g,
  rockType: /Rock:<\/strong><br><small>(.*)<\/small>/g,
  long: /data-osx="([-\.\d]+)"/g,
  lat: /data-osy="([-\.\d]+)"/g,
  name: /href=".*">(.*)<\/a><br><span class="text-muted small"><\/span>/g,
  numStaredClimbs:
    /Routes: <\/strong><span class="text-break">(\d+) \(\d+ total\)<\/span>/g,
  ukcLink: /href="(\/logbook\/crags[a-z\/_\-\d]+)/g,
};

const regexKeys = Object.keys(regexs);

console.log(regexKeys);

Arr.forEach((style) => {
  const trArray1: string[] =
    imports[style as keyof imports].html1.split('<tr ');
  const trArray2: string[] =
    imports[style as keyof imports].html2.split('<tr ');
  const trArray3: string[] =
    imports[style as keyof imports].html3.split('<tr ');

  const trArray = [...trArray1, ...trArray2, ...trArray3];

  const crags: crag[] = [];

  trArray.forEach((tableRow) => {
    if (tableRow) {
      const crag: crag = {
        aspect: '',
        rockType: '',
        long: '',
        lat: '',
        name: '',
        numStaredClimbs: '',
        ukcLink: '',
      };
      regexKeys.forEach((regexKey) => {
        const matchArray = [
          ...tableRow.matchAll(regexs[regexKey as keyof typeof regexs]),
        ][0];
        if (matchArray) {
          crag[regexKey as keyof typeof regexs] = matchArray[1];
        }
      });
      if (crag.name) {
        crags.push(crag);
      }
    }
  });

  const cragsFiltered = [...new Set(crags)];
  console.log(cragsFiltered[0]);

  writeFile(`./jsons/${style}_crags.json`, JSON.stringify(cragsFiltered));
});

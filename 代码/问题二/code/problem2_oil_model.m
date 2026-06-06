% Problem 2: medium and long term oil-price adjustment model.
% Run this script in the project root. It reads the Brent CSV and writes
% scenario paths to the results directory.

clear; clc;

csvPath = "/Users/hybuzhy/Documents/Mathematical modeling/附件1.布伦特原油期货主力合约价格数据.csv";
outDir = "results";
if ~exist(outDir, "dir")
    mkdir(outDir);
end

data = readtable(csvPath, "TextType", "string");
latestClose = data.close(find(~isnan(data.close), 1, "last"));

base = defaultParams();
base.initial_price = latestClose;

scenarioNames = ["baseline", "optimistic", "pessimistic"];
params = {base, optimisticParams(base), pessimisticParams(base)};

summaryScenario = strings(numel(scenarioNames), 1);
summaryDay90 = zeros(numel(scenarioNames), 1);
summaryDay180 = zeros(numel(scenarioNames), 1);
summaryEq180 = zeros(numel(scenarioNames), 1);
summaryStock180 = zeros(numel(scenarioNames), 1);
summaryRisk180 = zeros(numel(scenarioNames), 1);

figure("Position", [100, 100, 900, 520]);
hold on;
for i = 1:numel(scenarioNames)
    rows = simulatePath(params{i});
    outputPath = fullfile(outDir, "problem2_" + scenarioNames(i) + "_path_matlab.csv");
    writetable(rows, outputPath);

    plot(rows.day, rows.price, "LineWidth", 1.8);
    summaryScenario(i) = scenarioNames(i);
    summaryDay90(i) = rows.price(1);
    summaryDay180(i) = rows.price(end);
    summaryEq180(i) = rows.equilibrium_price(end);
    summaryStock180(i) = rows.commercial_stock(end);
    summaryRisk180(i) = rows.risk_premium(end);
end
hold off;
grid on;
xlabel("Days after blockade");
ylabel("Brent price (USD/barrel)");
title("Problem 2: Medium- and long-term Brent price adjustment");
legend(scenarioNames, "Location", "best");
saveas(gcf, fullfile(outDir, "problem2_price_paths_matlab.png"));

summary = table(summaryScenario, summaryDay90, summaryDay180, summaryEq180, ...
    summaryStock180, summaryRisk180, ...
    "VariableNames", ["scenario", "day90_price", "day180_price", ...
    "day180_equilibrium", "day180_stock", "day180_risk"]);
writetable(summary, fullfile(outDir, "problem2_summary_matlab.csv"));
disp(summary);

function p = defaultParams()
    p.baseline_supply = 100.0;
    p.baseline_demand = 100.0;
    p.baseline_price = 75.0;
    p.initial_price = 95.25;
    p.long_run_elasticity = -0.18;
    p.adjustment_speed = 0.16;
    p.blockade_loss = 16.0;
    p.bypass_day90 = 2.4;
    p.bypass_cap = 3.0;
    p.extra_output_day90 = 1.0;
    p.extra_output_cap = 4.5;
    p.strategic_release_day90 = 5.0;
    p.strategic_release_day180 = 2.0;
    p.commercial_stock_day90 = 355.0;
    p.commercial_draw_cap_day90 = 2.0;
    p.commercial_draw_cap_day180 = 0.5;
    p.demand_adaptation_day90 = 0.0;
    p.demand_adaptation_day180 = 0.0;
    p.risk_stock_threshold = 90.0;
    p.risk_premium_cap = 38.0;
    p.start_day = 90;
    p.end_day = 180;
end

function p = optimisticParams(base)
    p = base;
    p.blockade_loss = 14.0;
    p.extra_output_cap = 5.5;
    p.strategic_release_day180 = 3.0;
    p.commercial_stock_day90 = 390.0;
end

function p = pessimisticParams(base)
    p = base;
    p.blockade_loss = 18.0;
    p.extra_output_cap = 3.0;
    p.strategic_release_day180 = 1.0;
    p.commercial_stock_day90 = 130.0;
    p.risk_premium_cap = 52.0;
end

function y = ramp(day, startDay, endDay, startValue, endValue)
    if day <= startDay
        y = startValue;
    elseif day >= endDay
        y = endValue;
    else
        w = (day - startDay) / (endDay - startDay);
        y = startValue + w * (endValue - startValue);
    end
end

function premium = riskPremium(stock, p)
    if stock >= p.risk_stock_threshold
        premium = 0.0;
    else
        shortageRatio = 1.0 - max(stock, 0.0) / p.risk_stock_threshold;
        premium = p.risk_premium_cap * shortageRatio ^ 2;
    end
end

function price = equilibriumPrice(basePrice, demandScale, effectiveSupply, elasticity)
    price = basePrice * (effectiveSupply / demandScale) ^ (1.0 / elasticity);
end

function rows = simulatePath(p)
    n = p.end_day - p.start_day + 1;
    day = zeros(n, 1);
    price = zeros(n, 1);
    equilibrium_price = zeros(n, 1);
    target_price = zeros(n, 1);
    risk_premium = zeros(n, 1);
    commercial_stock = zeros(n, 1);
    bypass = zeros(n, 1);
    extra_output = zeros(n, 1);
    strategic_release = zeros(n, 1);
    commercial_draw = zeros(n, 1);
    demand_scale = zeros(n, 1);
    nonstock_supply = zeros(n, 1);
    effective_supply = zeros(n, 1);
    residual_gap = zeros(n, 1);

    currentPrice = p.initial_price;
    stock = p.commercial_stock_day90;

    for k = 1:n
        d = p.start_day + k - 1;
        day(k) = d;
        bypass(k) = ramp(d, p.start_day, p.end_day, p.bypass_day90, p.bypass_cap);
        extra_output(k) = ramp(d, p.start_day, p.end_day, p.extra_output_day90, p.extra_output_cap);
        strategic_release(k) = ramp(d, p.start_day, p.end_day, p.strategic_release_day90, p.strategic_release_day180);
        drawCap = ramp(d, p.start_day, p.end_day, p.commercial_draw_cap_day90, p.commercial_draw_cap_day180);
        demandAdaptation = ramp(d, p.start_day, p.end_day, p.demand_adaptation_day90, p.demand_adaptation_day180);

        demand_scale(k) = p.baseline_demand - demandAdaptation;
        nonstock_supply(k) = p.baseline_supply - p.blockade_loss + bypass(k) + extra_output(k) + strategic_release(k);
        physicalGap = max(0.0, demand_scale(k) - nonstock_supply(k));
        commercial_draw(k) = min([drawCap, stock, physicalGap]);
        effective_supply(k) = nonstock_supply(k) + commercial_draw(k);
        residual_gap(k) = max(0.0, demand_scale(k) - effective_supply(k));

        equilibrium_price(k) = equilibriumPrice(p.baseline_price, demand_scale(k), effective_supply(k), p.long_run_elasticity);
        risk_premium(k) = riskPremium(stock, p);
        target_price(k) = equilibrium_price(k) + risk_premium(k);
        currentPrice = currentPrice + p.adjustment_speed * (target_price(k) - currentPrice);
        stock = max(0.0, stock - commercial_draw(k));

        price(k) = currentPrice;
        commercial_stock(k) = stock;
    end

    rows = table(day, price, equilibrium_price, target_price, risk_premium, commercial_stock, ...
        bypass, extra_output, strategic_release, commercial_draw, demand_scale, ...
        nonstock_supply, effective_supply, residual_gap);
end
